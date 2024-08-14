# stdlib
import logging
from math import ceil
from typing import List
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse
# local
from .server_type import ServerType
from .storage_type import StorageType
from iaas import state
from iaas.utils import dot_product, magnitude

__all__ = [
    'Server',
]


class ServerManager(BaseManager):
    """
    Manager for Server which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'storage_type',
            'type',
        ).prefetch_related(
            'devices',
            'interfaces',
            'guest_vms',
        )


class Server(BaseModel):
    """
    A Server object represents a physical Server in a region.
    Servers are of a certain type, indicating the type of images they can host.
    """
    # Oversubscription Value
    OVERSUBSCRIPTION_VALUE = 8

    # Limit Variables
    DISK_BASE_LIMIT = 100
    RAM_BASE_LIMIT = 8
    CPU_CREATE_LIMIT = 0.77
    DISK_CREATE_LIMIT = 0.77
    RAM_CREATE_LIMIT = 0.85
    CPU_UPDATE_LIMIT = 1.00
    DISK_UPDATE_LIMIT = 0.9
    RAM_UPDATE_LIMIT = 0.95

    asset_tag = models.IntegerField(null=True)
    cores = models.IntegerField()
    enabled = models.BooleanField(default=True)
    gb = models.IntegerField()
    model = models.CharField(max_length=64)
    ram = models.IntegerField()
    region_id = models.IntegerField()
    storage_type = models.ForeignKey(StorageType, on_delete=models.PROTECT)
    type = models.ForeignKey(ServerType, null=True, related_name='servers', on_delete=models.PROTECT)

    objects = ServerManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'server'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='server_id'),
            models.Index(fields=['asset_tag'], name='server_asset_tag'),
            models.Index(fields=['cores'], name='server_cores'),
            models.Index(fields=['deleted'], name='server_deleted'),
            models.Index(fields=['enabled'], name='server_enabled'),
            models.Index(fields=['gb'], name='server_gb'),
            models.Index(fields=['model'], name='server_model'),
            models.Index(fields=['ram'], name='server_ram'),
            models.Index(fields=['region_id'], name='server_region_id'),
        ]
        ordering = ['region_id']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RouterResource view for this Server record
        :return: A URL that corresponds to the views for this Server record
        """
        return reverse('server_resource', kwargs={'pk': self.pk})

    @property
    def vcpus(self) -> int:
        """
        Returns the number of vcpus in the server, by multiplying the number of cores by the oversubscription ratio
        """
        return self.cores * self.OVERSUBSCRIPTION_VALUE

    @property
    def hostname(self) -> str:
        """
        Get a string containing the ip address and hostname (if the server has one)
        """
        interface_found = False
        # Get the first interface with a hostname, or the first with an ip address if none have a hostname
        hostname_query = self.interfaces.exclude(hostname='')
        if hostname_query.exists():
            interface_found = True
            interface = hostname_query.first()

        # If no hostname exists, just get the first one with an ip
        ip_address_query = self.interfaces.filter(ip_address__isnull=False)
        if ip_address_query.exists():
            interface_found = True
            interface = ip_address_query.first()

        if not interface_found:
            return ''

        # Return a string based on what fields are available
        if interface.ip_address is not None and interface.hostname != '':
            # Return a string containing both ip address and hostname
            return f'{interface.ip_address} / {interface.hostname}'
        elif interface.ip_address is not None:
            # Return a string containing just the ip_address
            return interface.ip_address
        elif interface.hostname != '':
            # Return a string that contains just the hostname
            return interface.hostname
        else:
            # Return an empty string since we can't find anything
            return ''  # pragma: no cover

    @property
    def vcpus_for_create(self) -> int:
        """
        Using the limit values, get the remaining amount of cpus available for a create request
        """
        return ceil(self.vcpus * self.CPU_CREATE_LIMIT)

    @property
    def ram_for_create(self) -> int:
        """
        Using the limit values, get the remaining amount of ram available for a create request
        """
        total = self.ram - self.RAM_BASE_LIMIT
        return ceil(total * self.RAM_CREATE_LIMIT)

    @property
    def gb_for_create(self) -> int:
        """
        Using the limit values, get the remaining amount of gb available for a create request
        """
        total = self.gb - self.DISK_BASE_LIMIT
        return ceil(total * self.DISK_CREATE_LIMIT)

    @property
    def vcpus_for_update(self) -> int:
        """
        Using the limit values, get the remaining amount of cpus available for a update request
        """
        return ceil(self.vcpus * self.CPU_UPDATE_LIMIT)

    @property
    def ram_for_update(self) -> int:
        """
        Using the limit values, get the remaining amount of ram available for a update request
        """
        total = self.ram - self.RAM_BASE_LIMIT
        return ceil(total * self.RAM_UPDATE_LIMIT)

    @property
    def gb_for_update(self) -> int:
        """
        Using the limit values, get the remaining amount of gb available for a update request
        """
        total = self.gb - self.DISK_BASE_LIMIT
        return ceil(total * self.DISK_UPDATE_LIMIT)

    @property
    def gb_in_use(self) -> int:
        """
        Return the total amount of disk space on the server currently in use by VMs
        """
        return self.guest_vms.exclude(
            state=state.CLOSED,
        ).aggregate(total_gb=Coalesce(models.Sum('storages__gb'), models.Value(0)))['total_gb']

    @property
    def ram_in_use(self) -> int:
        """
        Return the total amount of RAM on the server currently in use by VMs
        """
        return self.guest_vms.exclude(
            state=state.CLOSED,
        ).aggregate(sum=Coalesce(models.Sum('ram'), models.Value(0)))['sum']

    @property
    def vcpus_in_use(self) -> int:
        """
        Return the total amount of vCPUs on the server currently in use by VMs
        """
        return self.guest_vms.exclude(
            state=state.CLOSED,
        ).aggregate(sum=Coalesce(models.Sum('cpu'), models.Value(0)))['sum']

    @property
    def klinavicius(self) -> List[int]:
        """
        Returns the current klinavicius vector for the Server.
        This is a vector containing the values of [ram, gb, vcpus] after taking into account the VMs currently on
        the Server

        Since this is only used in create, this will take the create values into account
        """
        return [
            self.ram_for_create - self.ram_in_use,
            self.gb_for_create - self.gb_in_use,
            self.vcpus_for_create - self.vcpus_in_use,
        ]

    def get_suitability(self, vm_klinavicius: List[int]) -> float:
        """
        Find if this server is a good match for the passed VM. If the VM and servers are represented as vectors, the
        most suitable server is the one that creates the smallest angle with the VM. This angle can be found by
        calculating the dot (inner) product of the two vectors. Dot product is written as:

         |V| cos(theta) = ( V dot S ) / |S|
            V - VM's Klinavicius vector
            S - Server's Klinavicius vector
            |V| - Magnitude of V
            |S| - Magnitude of S
            V dot S - Dot product between V and S
            theta - The angle between V and S

        Since this method will be run one VM against different server records, we'll return |V| cos(theta) for the
        comparisons since |V| will be constant.

        :param vm_klinavicius: The klinavicius vector for the VM being tested on this Server.
        :returns: A value between 0 and |V|, with a larger number implying this server is a good match for the VM
        """
        server_klinavicius = self.klinavicius
        # Ensure that none of the requirements outweigh what the server has available
        for i in range(len(vm_klinavicius)):
            if vm_klinavicius[i] > server_klinavicius[i]:
                return float('-inf')

        suitability = float('-inf')
        logger = logging.getLogger('iaas.server.get_suitability')
        try:
            suitability = dot_product(vm_klinavicius, server_klinavicius) / magnitude(server_klinavicius)
        except ValueError:  # pragma: no cover
            logger.error(
                'Could not compute suitability of VM',
                exc_info=True,
                extra={'server_id': self.pk, 'sever_resources': server_klinavicius, 'vm_resources': vm_klinavicius},
            )

        return suitability
