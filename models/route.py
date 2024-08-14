# stdlib
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
import netaddr
# local
from .subnet import Subnet
from .vpn import VPN

__all__ = [
    'Route',
]


class RouteManager(BaseManager):
    """
    Manager for VPN Route which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'local_subnet',
        )


class Route(BaseModel):
    """
    A VPN route object represents a route between the project's local subnet and customer's remote subnet.
    """
    # Constant /24 subnets available per region for Dynamic Secure Connect VPNs.
    # Currently we are only using the RFC1918 address range 172.16.0.0/12 which yields 4096 /24 subnets.

    # List items are IPNetwork
    DYNAMIC_REMOTE_SUBNET_NETWORKS = list(netaddr.IPNetwork('172.16.0.0/12').subnet(24))
    # List items are strings
    DYNAMIC_REMOTE_SUBNET_LIST = [str(network) for network in DYNAMIC_REMOTE_SUBNET_NETWORKS]

    local_subnet = models.ForeignKey(Subnet, on_delete=models.CASCADE)
    remote_subnet = models.CharField(max_length=49)
    vpn = models.ForeignKey(VPN, related_name='routes', on_delete=models.CASCADE)

    objects = RouteManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'route'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='route_id'),
        ]
        ordering = ['remote_subnet']
