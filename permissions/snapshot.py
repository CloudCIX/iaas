# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import Snapshot, VM
from iaas.utils import get_addresses_in_member

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.vm methods
    """

    @staticmethod
    def create(request: Request, obj: VM) -> Optional[Http403]:
        """
        The request to create a Snapshot is valid if:
        - The requesting User's Address owns the Snapshot's VM.
        """
        if request.user.address['id'] != obj.project.address_id:
            return Http403(error_code='iaas_snapshot_create_201')

        return None

    @staticmethod
    def head(request: Request, obj: Snapshot, span: Span) -> Optional[Http403]:
        """
        The request to access a Snapshot is valid if:
        - The User is the Robot from the region of the Snapshot VM of the Project.
        - The requesting User's Address owns the Snapshot's VM.
        - The requesting user is global active and Snapshot's VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403()
        elif request.user.address['id'] != obj.vm.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.vm.project.address_id not in get_addresses_in_member(request, span):
                    return Http403()
            else:
                return Http403()

        return None

    @staticmethod
    def read(request: Request, obj: Snapshot, span: Span) -> Optional[Http403]:
        """
        The request to read Snapshot is valid if;
        - The User is the Robot from the region of the Snapshot VM of the Project.
        - The requesting User's Address owns the Snapshot's VM.
        - The requesting user is global active and Snapshot's VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if request.user.robot:
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403(error_code='iaas_snapshot_read_201')
        elif request.user.address['id'] != obj.vm.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.vm.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_snapshot_read_202')
            else:
                return Http403(error_code='iaas_snapshot_read_203')

        return None

    @staticmethod
    def tree_read(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to read Snapshot Tree is valid if;
        - The requesting User's Address owns the VM.
        - The requesting user is global active and the VM is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if request.user.address['id'] != obj.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_snapshot_tree_read_201')
            else:
                return Http403(error_code='iaas_snapshot_tree_read_202')

        return None

    @staticmethod
    def update(request: Request, obj: Snapshot) -> Optional[Http403]:
        """
        The request to update a Snapshot is valid if:
        - The User is the Robot from the region of the Snapshot VM of the Project.
        - The requesting User's Address owns the Snapshot's VM.
        """
        if request.user.robot:
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403(error_code='iaas_snapshot_update_201')
        else:
            if request.user.address['id'] != obj.vm.project.address_id:
                return Http403(error_code='iaas_snapshot_update_202')

        return None
