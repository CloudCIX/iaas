# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import VM
from iaas.utils import get_addresses_in_member

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.vm methods
    """

    @staticmethod
    def head(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to access VM is valid if;
        - The User is the Robot from the region of the VM of the Project.
        - The requesting User's Address owns the VM.
        - The requesting User is global active and the VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403()
        elif obj.project.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403()
            else:
                return Http403()

        return None

    @staticmethod
    def read(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to read VM is valid if;
        - The User is the Robot from the region of the VM of the Project.
        - The requesting User's Address owns the VM.
        - The requesting User is global active and the VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_vm_read_201')
        elif obj.project.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_vm_read_202')
            else:
                return Http403(error_code='iaas_vm_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: VM) -> Optional[Http403]:
        """
        The request to update a VM is valid if:
        - The User is the Robot from the region of the VM of the Project.
        - The requesting User's Address owns the VM
        """
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_vm_update_201')
        else:
            if request.user.address['id'] != obj.project.address_id:
                return Http403(error_code='iaas_vm_update_202')

        return None
