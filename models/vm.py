# stdlib
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional
import uuid
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse
# local
from iaas import skus, state as states
from .billable_model import BillableModelMixin
from .image import Image
from .project import Project
from .server import Server
from .subnet import Subnet

__all__ = [
    'VM',
]

SIXTEEN_KB = 16 * 1024


class VMManager(BaseManager):
    """
    Manager for VM which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'image',
            'gateway_subnet',
            'project',
            'server',
            'server__storage_type',
            'server__type',
        ).prefetch_related(
            'backups',
            'history',
            'snapshots',
            'storages',
            'server__interfaces',
            'vm_ips',
        )


class VM(BaseModel, BillableModelMixin):
    """
    A VM object represents a VM in a Cloud Project.
    """
    cpu = models.IntegerField()
    dns = models.TextField()
    image = models.ForeignKey(Image, on_delete=models.PROTECT)
    gateway_subnet = models.ForeignKey(Subnet, null=True, on_delete=models.PROTECT)
    gpu = models.IntegerField(default=0)
    guid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='vms')
    public_key = models.TextField(null=True)
    ram = models.IntegerField()
    server = models.ForeignKey(Server, related_name='guest_vms', on_delete=models.PROTECT)
    state = models.IntegerField(default=states.IN_API)  # Start states at -1 instead of 0
    userdata = models.CharField(max_length=SIXTEEN_KB)

    objects = VMManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'vm'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='vm_id'),
            models.Index(fields=['deleted'], name='vm_deleted'),
            models.Index(fields=['name'], name='vm_name'),
            models.Index(fields=['state'], name='vm_state'),
        ]
        ordering = ['name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the VMResource view for this VM record
        :return: A URL that corresponds to the views for this VM record
        """
        return reverse('vm_resource', kwargs={'pk': self.pk})

    @property
    def available_devices(self) -> Optional[int]:
        """
        The number of devices curently available to be assigned to VM.
        None will be returned it the VMs server does not have any devices
        """
        device_list = list(self.server.devices.iterator())
        if len(device_list) == 0:
            return None
        devices = 0
        for device in device_list:
            if device.vm_id is None:
                devices += 1
        return devices

    def can_update(self) -> bool:
        """
        Can this VM currently be updated?
        """
        # Use the User state change map to determine if the update from current state to
        # RUNNING_UPDATE or QUIESCED_UPDATE is allowed
        return states.RUNNING_UPDATE in states.USER_STATE_MAP.get(self.state, {}) or \
            states.QUIESCED_UPDATE in states.USER_STATE_MAP.get(self.state, {})

    @property
    def scrub_queue_time_passed(self):
        if self.state == states.SCRUB_QUEUE:
            return self.updated + timedelta(hours=self.project.grace_period) < datetime.now()
        return False

    def set_deleted(self):
        """
        Delete the VM, and delete the IP Address records that are related to it
        """
        for ip in self.vm_ips.all():
            ip.cascade_delete()

    def snapshots_stable(self) -> bool:
        """
        Determine if the VM instance's Snapshots is stable.

        The Snapshots are stable if they are all in stable states;
            - RUNNING
            - QUIESCED
            - SCRUB_QUEUE
            - CLOSED
        """

        return not self.snapshots.exclude(state__in=states.STABLE_STATES).exists()

    @property
    def stable(self) -> bool:
        """
        Determine if the VM instance is stable.

        The VM is stable if it, and it's infrastructure are in stable states;
            - RUNNING
            - QUIESCED
            - SCRUB_QUEUE
            - CLOSED
        """

        return self.state in states.STABLE_STATES and self.snapshots_stable()

    # Define the billable model methods
    def get_label(self) -> str:
        if self.name:
            return f'VM #{self.pk} - "{self.name}"'
        return f'VM #{self.pk}'

    def get_skus(self) -> Dict[str, Callable[[models.Model], int]]:
        """
        Build a map of SKU strings to a lambda that returns the current quantity of the field
        """
        image_sku = skus.IMAGE_SKU_MAP.get(self.image.pk, f'IMAGE_{skus.DEFAULT}')
        sku_map = {image_sku: lambda vm: 1}
        if 'phantom' in image_sku.lower():
            return sku_map

        # Start defining the SKUs
        sku_map.update({
            skus.RAM_001: lambda vm: vm.ram,
            skus.VCPU_001: lambda vm: vm.cpu,
            # NAT is based on the presence of an IP Address on this VM that has a Public IP Address
            skus.NAT_001: lambda vm: vm.vm_ips.filter(public_ip__isnull=False).count(),
        })

        # Add the keys that are programmatically based on the state of this VM
        storage_type_sku = skus.STORAGE_SKU_MAP.get(self.server.storage_type.pk, f'ST_{skus.DEFAULT}')
        sku_map[storage_type_sku] = (
            lambda vm: vm.storages.aggregate(total_gb=Coalesce(models.Sum('gb'), models.Value(0)))['total_gb']
        )
        # Device SKUs
        try:
            device = list(self.server.devices.iterator())[0]
            sku_map[device.device_type.sku] = lambda vm: vm.gpu
        except IndexError:
            # Server has no devices so no need to add to BOM of VM
            pass

        return sku_map
