# stdlib
from datetime import datetime
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .router import Router
from .subnet import Subnet
from .vm import VM

__all__ = [
    'IPAddress',
]


class IPAddressManager(BaseManager):
    """
    Manager for IPAddress that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'subnet',
            'subnet__allocation',
            'subnet__allocation__asn',
            'public_ip',
        )


class IPAddress(BaseModel):
    """

    """
    # Fields
    address = models.GenericIPAddressField()
    cloud = models.BooleanField(default=False)  # Indicates if the IP Address is related to CloudCIX
    credentials = models.CharField(max_length=64, default='')  # Credentials of the server this address is assigned to
    location = models.CharField(max_length=64, default='')
    modified_by = models.IntegerField(null=True)
    name = models.CharField(max_length=64, default='')
    ping = models.BooleanField(default=False)
    # As far as I can tell, NAT links will only ever be One-To-One or None
    # Also, the way I see it, if you delete the public IP, it should do nothing to the private IP
    public_ip = models.OneToOneField('self', on_delete=models.SET_NULL, null=True)
    router = models.ForeignKey(Router, related_name='router_ips', on_delete=models.CASCADE, null=True)
    scan = models.BooleanField(default=False)
    subnet = models.ForeignKey(Subnet, related_name='ip_addresses', on_delete=models.PROTECT)
    vm = models.ForeignKey(VM, related_name='vm_ips', on_delete=models.CASCADE, null=True)

    # Use the new Manager
    objects = IPAddressManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'ip_address'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='ip_address_id'),
            models.Index(fields=['address'], name='ip_address_address'),
            models.Index(fields=['cloud'], name='ip_address_cloud'),
            models.Index(fields=['created'], name='ip_address_created'),
            models.Index(fields=['deleted'], name='ip_address_deleted'),
            models.Index(fields=['name'], name='ip_address_name'),
            models.Index(fields=['ping'], name='ip_address_ping'),
            models.Index(fields=['scan'], name='ip_address_scan'),
            models.Index(fields=['updated'], name='ip_address_updated'),
        ]
        ordering = ['address']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the IPAddressResource view for this IPAddress record
        :return: A URL that corresponds to the views for this IPAddress record
        """
        return reverse('ip_address_resource', kwargs={'pk': self.pk})

    def cascade_delete(self):
        """
        Following the pattern for ASN, Allocation, and Subnet, this method handles deletion of an IPAddress record.
        Deletes the record and it's public record, if one exists.
        """
        deltime = datetime.utcnow()
        if self.public_ip is not None:
            self.public_ip.deleted = deltime
            self.public_ip.save()
        self.deleted = deltime
        self.save()
