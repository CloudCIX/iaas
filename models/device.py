# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .device_type import DeviceType
from .server import Server
from .vm import VM

__all__ = [
    'Device',
]


class DeviceManager(BaseManager):
    """
    Manager for Device that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'device_type',
            'vm',
        )


class Device(BaseModel):
    """
    A Device is an object external to a VM that can be attached to provide extended functionality
    """
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    id_on_host = models.CharField(max_length=12)
    server = models.ForeignKey(Server, related_name='devices', on_delete=models.CASCADE)
    vm = models.ForeignKey(VM, on_delete=models.DO_NOTHING, null=True)

    objects = DeviceManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'device'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='device_id'),
        ]
        ordering = ['id_on_host']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the DevcieResource view for this Device record
        :return: A URL that corresponds to the views for this Device record
        """
        return reverse('device_resource', kwargs={'pk': self.pk})
