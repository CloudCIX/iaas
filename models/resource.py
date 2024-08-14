# stdlib
from typing import Callable, Dict, Optional
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .project import Project
from iaas import state as states, resource_type as resource_types
from iaas.models import BillableModelMixin


__all__ = [
    'Resource',
]


RESOURCE_URL_MAP = {
    resource_types.CEPH: 'ceph_resource',
}


class ResourceManager(BaseManager):
    """
    Manager for Resources that pre-fetches foreign keys and One-to-One relations
    """

    def __init__(self, resource_type: Optional[int] = None):
        super(ResourceManager, self).__init__()
        self._resource_type = resource_type

    def create(self, *args, **kwargs):
        if 'resource_type' not in kwargs:
            # Use the default if one was given
            kwargs['resource_type'] = self._resource_type
        return super(ResourceManager, self).create(*args, **kwargs)

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        query = super().get_queryset().select_related(
            # Foreign Keys
            'project',
        )
        if self._resource_type is not None:
            query = query.filter(resource_type=self._resource_type)
        return query


class Resource(BaseModel, BillableModelMixin):
    """
    Defines any entity that a User can create and that has state.
    Acts as an interface for calculating billing data.
    """
    name = models.CharField(max_length=128)
    parent_id = models.IntegerField(null=True)
    project = models.ForeignKey(Project, related_name='resources', on_delete=models.CASCADE)
    resource_type = models.IntegerField()
    state = models.IntegerField(default=states.IN_API)

    objects = ResourceManager()
    cephs = ResourceManager(resource_type=resource_types.CEPH)

    new_boms: Optional[Dict] = None
    specs: Optional[Dict] = None

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'resource'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='resource_id'),
        ]
        ordering = ['created']

    def get_label(self) -> str:
        """
        Get the label that will identify this resource on a CloudBill invoice
        """
        if self.name:
            return f'Resource #{self.pk} - "{self.name}"'
        return f'Resource #{self.pk}'

    def get_absolute_url(self) -> str:
        url_name = RESOURCE_URL_MAP[self.resource_type]
        return reverse(url_name, kwargs={'pk': self.pk})

    def get_skus(self) -> Dict[str, Callable[[models.Model], int]]:
        # Get the current state of the Resource and overwrite with any new boms
        skus = dict()
        for bom in self.get_specs():
            skus[bom.sku] = lambda _: bom.quantity

        if self.new_boms is None:
            self.new_boms = {}
        for sku, quantity in self.new_boms.items():
            skus[sku] = lambda _: quantity

        return skus

    def get_specs(self):
        if self.specs is None:
            self._reload_specs()
        return self.specs

    def _reload_specs(self):
        # Load the latest BoM records onto the Resource
        self.specs = self.skus.all().order_by('sku', '-created').distinct('sku')

    def get_current_quantity(self, sku: str) -> Optional[int]:
        for s in self.get_specs():
            if s.sku == sku:
                return s.quantity
        return None  # pragma: no cover

    def refresh_from_db(self):
        super().refresh_from_db()
        self._reload_specs()

    @property
    def scrub_queue_time_passed(self):
        return False
