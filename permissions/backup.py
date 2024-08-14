# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
from datetime import datetime
# local
from iaas.models import Backup, VM
from iaas.utils import get_addresses_in_member


__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.backup methods
    """

    @staticmethod
    def create(request: Request, obj: VM) -> Optional[Http403]:
        """
        The request to create a Backup is valid if:
        - The requesting User's Address owns the Backup's VM.
        - The requesting user is public.
        """
        if request.user.address['id'] != obj.project.address_id:
            return Http403(error_code='iaas_backup_create_201')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_backup_create_202')

        return None

    @staticmethod
    def read(request: Request, obj: Backup, span: Span) -> Optional[Http403]:
        """
        The request to read Backup is valid if;
        - The requesting User is the Robot from the region of the Backup VM of the Project.
        - The requesting User's Address owns the Backup's VM.
        - The requesting User is global active and Backup's VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403(error_code='iaas_backup_read_201')
        elif request.user.address['id'] != obj.vm.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.vm.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_backup_read_202')
            else:
                return Http403(error_code='iaas_backup_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: Backup, current_time_valid: datetime, time_valid: datetime) -> Optional[Http403]:
        """
        The request to update a Backup is valid if:
        - The requesting User is the Robot from the region of the Backup's project.
        - The requesting User's Address owns the Backup's VM.
        - The requesting user is public.
        """
        if request.user.robot:
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403(error_code='iaas_backup_update_201')
        elif request.user.address['id'] != obj.vm.project.address_id:
            return Http403(error_code='iaas_backup_update_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_backup_update_203')

        if current_time_valid == time_valid:
            return None

        if not request.user.robot:
            return Http403(error_code='iaas_backup_update_204')

        return None
