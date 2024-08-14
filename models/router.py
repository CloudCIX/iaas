# stdlib
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from iaas import state


__all__ = [
    'Router',
]


class RouterManager(BaseManager):
    """
    Manager for Router that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'router_ips',
            'virtual_routers',
        )


class Router(BaseModel):
    """
    A Router object represents a physical Router in a region.
    Routers are of a specific model, and have a set of ports that implement the defined port functions for the model.
    """
    asset_tag = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)  # A capacity of None allows infinite virtual_routers
    credentials = models.CharField(max_length=128, null=True)
    enabled = models.BooleanField(default=True)
    management_interface = models.CharField(max_length=20, null=True)
    model = models.CharField(max_length=64, default='')
    oob_interface = models.CharField(max_length=20, null=True)
    public_interface = models.CharField(max_length=20, null=True)
    private_interface = models.CharField(max_length=20, null=True)
    region_id = models.IntegerField()
    router_oob_interface = models.CharField(max_length=20, null=True)
    username = models.CharField(max_length=250, null=True)

    objects = RouterManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'router'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='router_id'),
            models.Index(fields=['asset_tag'], name='router_asset_tag'),
            models.Index(fields=['capacity'], name='router_capacity'),
            models.Index(fields=['deleted'], name='router_deleted'),
            models.Index(fields=['enabled'], name='router_enabled'),
            models.Index(fields=['region_id'], name='router_region_id'),
        ]
        ordering = ['region_id']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RouterResource view for this Router record
        :return: A URL that corresponds to the views for this Router record
        """
        return reverse('router_resource', kwargs={'pk': self.pk})

    def get_public_port_ips(self):
        """
        Returns a list of all the IP Addresses that is configured on the routers public port
        """
        return list(self.router_ips.values_list('address', flat=True).iterator())

    def get_subnets(self):
        """
        Returns a list of all the Subnet address ranges that is configured on the router.
        """
        return list(self.router_subnets.values_list('address_range', flat=True).iterator())

    def get_subnet_ids(self):
        """
        Returns a list of all the Subnet IDs that is configured on the router.
        """
        return list(self.router_subnets.values_list('pk', flat=True).iterator())

    @property
    def management_ip(self) -> str:
        """
        The Router's management IP address is used to access the Router by Robot and Api.
        This function gets all subnets under region_id address and filters out the one with ::/64 suffix which is
        the management network subnet of the region.
        :return: management_ip (type: str).
        """
        management_ip = ''
        # Filter router subnets for Region Assignment (a subnet ending with '/48)'
        # The management subnet for a /48  is the first /64
        objs = self.router_subnets.filter(
            address_id=self.region_id,
            address_range__iendswith='/48',
        ).distinct()

        if objs.exists():
            management_subnet = objs.first().address_range
            management_ip = f'{management_subnet.split("/")[0]}10:0:1'

        return management_ip

    @property
    def capacity_available(self) -> int:
        """
        Return the capacity available on the Router for virtual routers
        :return: virtual_routers_in_use (type: int)
        """
        capacity_available = 0
        if self.capacity is not None:
            capacity_available = self.capacity - self.virtual_routers.exclude(state=state.CLOSED).count()

        return capacity_available
