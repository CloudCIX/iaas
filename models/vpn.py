# stdlib
from datetime import datetime
from typing import Callable, Dict
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from iaas import skus
from .billable_model import BillableModelMixin
from .virtual_router import VirtualRouter

__all__ = [
    'VPN',
]


class VPNManager(BaseManager):
    """
    Manager for VPN which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'routes',
            'vpn_history',
        )


class VPN(BaseModel, BillableModelMixin):
    """
    A VPN object represents a VPN connection between customer networks and a cloud subnet.
    """
    # Choices
    # Authentication algorithms
    SHA1 = 'sha1'
    SHA256 = 'sha-256'
    SHA384 = 'sha-384'
    HMAC_SHA1 = 'hmac-sha1-96'
    HMAC_SHA256 = 'hmac-sha-256-128'
    IKE_AUTHENTICATION_ALGORITHMS = {
        SHA1,
        SHA256,
        SHA384,
    }
    IPSEC_AUTHENTICATION_ALGORITHMS = {
        HMAC_SHA1,
        HMAC_SHA256,
    }

    # Diffie Helmen Groups
    DH_GROUP_1 = 'group1'
    DH_GROUP_2 = 'group2'
    DH_GROUP_5 = 'group5'
    DH_GROUP_19 = 'group19'
    DH_GROUP_20 = 'group20'
    DH_GROUP_24 = 'group24'
    DH_GROUPS = {
        DH_GROUP_1,
        DH_GROUP_2,
        DH_GROUP_5,
        DH_GROUP_19,
        DH_GROUP_20,
        DH_GROUP_24,
    }

    # Encryption Algorithms
    AES128 = 'aes-128-cbc'
    AES192 = 'aes-192-cbc'
    AES256 = 'aes-256-cbc'
    AES128G = 'aes-128-gcm'
    AES192G = 'aes-192-gcm'
    AES256G = 'aes-256-gcm'
    IKE_ENCRYPTION_ALGORITHMS = {
        AES128,
        AES192,
        AES256,
    }
    IPSEC_ENCRYPTION_ALGORITHMS = {
        AES128,
        AES192,
        AES256,
        AES128G,
        AES192G,
        AES256G,
    }

    # Establish time
    ESTABLISH_IMMEDIATELY = 'immediately'
    ESTABLISH_ON_TRAFFIC = 'on-traffic'
    ESTABLISH_TIMES = (
        (ESTABLISH_IMMEDIATELY, ESTABLISH_IMMEDIATELY),
        (ESTABLISH_ON_TRAFFIC, ESTABLISH_ON_TRAFFIC),
    )

    # PFS Groups
    PFS_GROUP_1 = 'group1'
    PFS_GROUP_2 = 'group2'
    PFS_GROUP_5 = 'group5'
    PFS_GROUP_14 = 'group14'
    PFS_GROUP_19 = 'group19'
    PFS_GROUP_20 = 'group20'
    PFS_GROUP_24 = 'group24'
    PFS_GROUPS = {
        PFS_GROUP_1,
        PFS_GROUP_2,
        PFS_GROUP_5,
        PFS_GROUP_14,
        PFS_GROUP_19,
        PFS_GROUP_20,
        PFS_GROUP_24,
    }

    # Ike Versions
    VERSION1 = 'v1-only'
    VERSION2 = 'v2-only'
    VERSIONS = (
        (VERSION1, VERSION1),
        (VERSION2, VERSION2),
    )

    # IKE Gateways
    GATEWAY_PUBLIC_IP = 'public_ip'
    GATEWAY_HOSTNAME = 'hostname'
    IKE_GATEWAY_TYPES = (
        (GATEWAY_PUBLIC_IP, GATEWAY_PUBLIC_IP),
        (GATEWAY_HOSTNAME, GATEWAY_HOSTNAME),
    )

    # VPN Types
    DYNAMIC_SECURE_CONNECT = 'dynamic_secure_connect'
    SITE_TO_SITE = 'site_to_site'
    TYPES = (
        (SITE_TO_SITE, SITE_TO_SITE),
        (DYNAMIC_SECURE_CONNECT, DYNAMIC_SECURE_CONNECT),
    )

    # Lifetimes
    LIFETIME_RANGE = range(180, 86401)

    # Stif Number
    STIF_NUMBER_RANGE = range(10000, 15000)

    description = models.TextField(null=True)
    dns = models.GenericIPAddressField(null=True)
    send_email = models.BooleanField(default=False)
    stif_number = models.IntegerField()
    traffic_selector = models.BooleanField(default=False)
    virtual_router = models.ForeignKey(
        VirtualRouter,
        on_delete=models.CASCADE,
        related_name='vpn_tunnels',
    )
    vpn_type = models.CharField(max_length=22, default='site_to_site', choices=TYPES)

    # IKE Fields
    ike_authentication = models.TextField()  # Array, comma separated
    ike_dh_groups = models.TextField()       # Array, comma separated
    ike_encryption = models.TextField()      # Array, comma separated
    ike_gateway_type = models.CharField(max_length=9, choices=IKE_GATEWAY_TYPES, default=GATEWAY_PUBLIC_IP)
    # either an ip or a valid hostname, based on the value of ike_gateway_value
    ike_gateway_value = models.TextField(default='')
    ike_lifetime = models.IntegerField(default=28800)
    ike_local_identifier = models.CharField(max_length=253, null=True)
    ike_pre_shared_key = models.CharField(max_length=255)
    ike_public_ip = models.GenericIPAddressField(null=True)
    ike_remote_identifier = models.CharField(max_length=253, null=True)
    ike_version = models.CharField(max_length=8, choices=VERSIONS)

    # IPSec Fields
    ipsec_authentication = models.TextField()      # Array, comma separated
    ipsec_encryption = models.TextField()          # Array, comma separated
    ipsec_establish_time = models.CharField(max_length=12, choices=ESTABLISH_TIMES)
    ipsec_pfs_groups = models.TextField(null=True)  # Array, comma separated (can be None)
    ipsec_lifetime = models.IntegerField(default=3600)

    objects = VPNManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'vpn'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='vpn_id'),
            models.Index(fields=['deleted'], name='vpn_deleted'),
            models.Index(fields=['ike_public_ip'], name='vpn_ike_public_io'),
        ]
        ordering = ['description']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the VPNResource view for this VPN record
        :return: A URL that corresponds to the views for this VPN record
        """
        return reverse('vpn_resource', kwargs={'pk': self.pk})

    def cascade_delete(self):
        """
        Set the deleted timestamp of this VPN to the current time, and call this method on all of the Routes belonging
        to this VPN
        """
        self.deleted = datetime.utcnow()
        self.save()

        # Also delete Routes and Clients
        for route in self.routes.all().iterator():
            route.deleted = datetime.utcnow()
            route.save()

        for client in self.vpn_clients.all().iterator():
            client.deleted = datetime.utcnow()
            client.save()

    # Define the billable model methods

    # Spoof state using the virtual router state
    @property
    def state(self) -> int:
        return self.virtual_router.state

    def get_label(self) -> str:
        return f'VPN #{self.pk}'

    def get_skus(self) -> Dict[str, Callable[[models.Model], int]]:
        """
        Build a map of SKU strings to a lambda that returns the current quantity of the field
        """
        # Figure out what the SKU Type we need is
        sku_name = skus.SITE_TO_SITE
        if self.vpn_type == self.DYNAMIC_SECURE_CONNECT:
            sku_name = skus.DYNAMIC_SECURE_CONNECT

        return {
            sku_name: lambda vpn: 1,
        }
