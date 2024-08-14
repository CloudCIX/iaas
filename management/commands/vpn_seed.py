# stdlib
from typing import List
# lib
from django.core.management.base import BaseCommand
# local
from iaas.models import (
    VPN,
)
from iaas import state
from iaas.controllers.helpers import get_ike_identifier


class Command(BaseCommand):
    can_import_settings = True
    help = (
        'A one-time command to create IKE local and remote identifier for exiting VPNs'
        ' which has null ike_local_identifier. '
    )

    def handle(self, *args, **options):
        """
        - Loop through the models that are not deleted and not in state CLOSED
        - If they have null ike_local_identifier update them with the identifier
        """
        self._handle_models(VPN.objects.filter(
            ike_local_identifier__isnull=True,
        ).exclude(virtual_router__state=state.CLOSED))

    def _handle_models(self, vpns: List[VPN]):
        """
        Generate ike identifier and update VPN
        """
        for vpn in vpns:
            # ike identifier method is in iaas.controllers.helpers
            identifier = get_ike_identifier(vpn)
            vpn.ike_local_identifier = f'local-{identifier}'
            vpn.ike_remote_identifier = f'remote-{identifier}'
            vpn.save()
