# stdlib
from typing import List
# lib
from django.core.management.base import BaseCommand
# local
from iaas.models import VM
from iaas import state
from iaas.utils import get_vm_interface_mac_address


class Command(BaseCommand):
    can_import_settings = True
    help = (
        'A one-time command to create mac addresses for VM Private IPs.'
    )

    def handle(self, *args, **options):
        """
        - Loop through the models that are not deleted and not in state CLOSED
        - For each ip in vm.ip_addresses, if it's subnet does not have a mac addresses assigned, assign and save
        """
        self._handle_models(VM.objects.filter(deleted__isnull=True).exclude(virtual_router__state=state.CLOSED))

    def _handle_models(self, vms: List[VM]):
        """
        Generate ike identifier and update VPN
        """
        for vm in vms:
            mac_address_subnets: List = []
            region_id = vm.project.region_id
            server_type_id = vm.server.type.id
            for ip in vm.vm_ips.all().iterator():
                if ip.subnet.pk not in mac_address_subnets:
                    ip.mac_address = get_vm_interface_mac_address(region_id, server_type_id, ip.id)
                    ip.save()
                    mac_address_subnets.append(ip.subnet.pk)
