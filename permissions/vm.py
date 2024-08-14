# stdlib
from typing import Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import VM

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.vm methods
    """

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to update a VM is valid if:
        - The requesting user is public
        """
        # The requesting user is public
        if request.user.is_private:
            return Http403(error_code='iaas_vm_create_201')
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
                # The requesting User is Global Active and the VM is owned by an Address in their Member.
                response = Membership.address.read(
                    token=request.user.token,
                    pk=obj.project.address_id,
                    span=span,
                )
                vm_member_id = -1
                if 200 == response.status_code:
                    vm_member_id = response.json()['content']['member_id']
                if request.user.member['id'] != vm_member_id:
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
        - The requesting user is public
        """
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_vm_update_201')
        elif request.user.address['id'] != obj.project.address_id:
            return Http403(error_code='iaas_vm_update_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_vm_update_203')

        return None
