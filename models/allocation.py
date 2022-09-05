# stdlib
from datetime import datetime
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
from rest_framework.request import Request
# local
from .asn import ASN

__all__ = [
    'Allocation',
]


class AllocationManager(BaseManager):
    """
    Manager for Allocation that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'asn',
        )


class Allocation(BaseModel):
    """
    An Allocation is a range of IP Addresses to an ASN by a Regional Internet Registry (RIR) such as RIPE.
    Only CIX can modify Allocation records, but they can be assigned to other Addresses who can then read them.
    """
    # Constants
    private_allocations = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '169.254.0.0/16']

    # Fields
    address_id = models.IntegerField(null=True)
    address_range = models.CharField(max_length=49)
    asn = models.ForeignKey(ASN, related_name='allocations', on_delete=models.PROTECT)
    modified_by = models.IntegerField(null=True)
    name = models.CharField(max_length=64)

    # Use the new Manager
    objects = AllocationManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'allocation'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='allocation_id'),
            models.Index(fields=['address_id'], name='allocation_address_id'),
            models.Index(fields=['address_range'], name='allocation_address_range'),
            models.Index(fields=['created'], name='allocation_created'),
            models.Index(fields=['deleted'], name='allocation_deleted'),
            models.Index(fields=['name'], name='allocation_name'),
            models.Index(fields=['updated'], name='allocation_updated'),
        ]
        ordering = ['address_range']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the AllocationResource view for this Allocation record
        :return: A URL that corresponds to the views for this Allocation record
        """
        return reverse('allocation_resource', kwargs={'pk': self.pk})

    def cascade_delete(self):
        """
        Set the deleted timestamp of this Allocation to the current time, and call this method on all of the Subnets
        belonging to this Allocation
        """
        self.deleted = datetime.utcnow()
        self.save()
        for subnet in self.subnets.iterator():
            subnet.cascade_delete()

    @classmethod
    def create_pseudo(cls, request: Request, asn: ASN):
        """
        Create the necessary private allocations for an ASN
        """
        for i, network in enumerate(cls.private_allocations):
            Allocation.objects.create(
                name=f'Private Range {i + 1}',
                address_range=str(network),
                asn=asn,
                modified_by=request.user.id,
                address_id=request.user.address['id'],
            )

    @property
    def subnets_in_use(self) -> int:
        """
        Return the count of all subnet records that are in use in this Allocation
        """
        return self.subnets.count()
