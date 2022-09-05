# stdlib
from datetime import datetime
from typing import List
# lib
from django.core.management.base import BaseCommand
# local
from iaas.models import (
    BillableModelMixin,
    VM,
    VPN,
)
from iaas import state


class Command(BaseCommand):
    can_import_settings = True
    help = (
        'A one-time command to create BOM entries for VMs created before the start date. '
    )
    start_date = datetime.strptime('01/09/2021 00:00:00', '%d/%m/%Y %H:%M:%S')

    def handle(self, *args, **options):
        """
        - Loop through the models that are not deleted and not in state CLOSED
        - If they don't have BOM models created, create one with the appropriate stats on the start date
        """
        self._handle_models(VM.objects.exclude(state=state.CLOSED))
        self._handle_models(VPN.objects.exclude(virtual_router__state=state.CLOSED))

    def _handle_models(self, objs: List[BillableModelMixin]):
        """
        Actually do the code in a model agnostic way, assuming the supplied queryset is of BillableModels
        """
        for obj in objs:
            if obj.skus.exists():
                continue

            # Use the method in BillableModelMixin to create the BOMs on the start date
            print(f'Creating BOM models for {obj.get_label()}')
            obj.create_boms(self.start_date)
