# stdlib
from datetime import datetime
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .allocation import Allocation
from .router import Router

__all__ = [
    'Subnet',
]


class SubnetManager(BaseManager):
    """
    Manager for Subnet that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'allocation',
            'allocation__asn',
            'parent',
        )


class Subnet(BaseModel):
    """
    A Subnet in the iaas API represents a networking Subnet, belonging to an Allocation.
    The owning Member has full control over their Subnets.
    """
    # Fields
    address_id = models.IntegerField(null=True)
    address_range = models.CharField(max_length=49)
    allocation = models.ForeignKey(Allocation, related_name='subnets', on_delete=models.PROTECT, null=True)
    cloud = models.BooleanField(default=False)
    gateway = models.GenericIPAddressField(null=True)
    modified_by = models.IntegerField(null=True)
    name = models.CharField(max_length=128, default='')
    parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.PROTECT)
    router = models.ForeignKey(Router, related_name='router_subnets', on_delete=models.CASCADE, null=True)
    virtual_router_id = models.IntegerField(null=True)
    vlan = models.IntegerField(null=True)
    vxlan = models.IntegerField(null=True)

    # Use the new Manager
    objects = SubnetManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'subnet'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='subnet_id'),
            models.Index(fields=['address_id'], name='subnet_address_id'),
            models.Index(fields=['address_range'], name='subnet_address_range'),
            models.Index(fields=['cloud'], name='subnet_cloud'),
            models.Index(fields=['created'], name='subnet_created'),
            models.Index(fields=['deleted'], name='subnet_deleted'),
            models.Index(fields=['gateway'], name='subnet_gateway'),
            models.Index(fields=['name'], name='subnet_name'),
            models.Index(fields=['updated'], name='subnet_updated'),
            models.Index(fields=['virtual_router_id'], name='subnet_virtual_router_id'),
            models.Index(fields=['vlan'], name='subnet_vlan'),
            models.Index(fields=['vxlan'], name='subnet_vxlan'),
        ]

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the SubnetResource view for this Subnet record
        :return: A URL that corresponds to the views for this Subnet record
        """
        return reverse('subnet_resource', kwargs={'pk': self.pk})

    @property
    def ips_in_use(self) -> int:
        """
        Return the count of all ip address records that are in use in this Subnet
        """
        return self.ip_addresses.count()

    @property
    def subnets_in_use(self) -> int:
        """
        Return the count of all subnet records that are in use in this Subnet
        """
        return self.children.count()

    def cascade_delete(self):
        """
        Set the deleted timestamp of this Subnet to the current time, and call this method on all of the IPAddresses
        and child Subnets belonging to this Subnet
        """
        self.deleted = datetime.utcnow()
        self.save()

        # Also delete IP Addresses
        for ip in self.ip_addresses.all().iterator():
            ip.cascade_delete()
