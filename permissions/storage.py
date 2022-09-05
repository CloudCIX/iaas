# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import VM
from iaas.utils import get_addresses_in_member


class Permissions:
    """
    Checks the permissions of the views.storage methods
    """

    @staticmethod
    def list(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to list Storage objects in a VM is valid if;
        - The requesting User owns the VM
        - The requesting user is global active and the VM belongs to an Address in their Member
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if request.user.address['id'] != obj.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_storage_list_201')
            else:
                return Http403(error_code='iaas_storage_list_202')

        return None

    @staticmethod
    def create(request: Request, obj: VM) -> Optional[Http403]:
        """
        The request to create a Storage object is valid if;
        - The requesting User owns the VM
        """
        if request.user.address['id'] != obj.project.address_id:
            return Http403(error_code='iaas_storage_create_201')

        return None

    @staticmethod
    def head(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to access a storage is valid if;
        - The requesting User owns the VM
        - The requesting user is global active and the VM belongs to an Address in their Member
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403()
        elif request.user.address['id'] != obj.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403()
            else:
                return Http403()
        return None

    @staticmethod
    def read(request: Request, obj: VM, span: Span) -> Optional[Http403]:
        """
        The request to read storage is valid if;
        - The requesting User owns the VM
        - The requesting user is global active and the VM belongs to an Address in their Member
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_storage_read_201')
        elif request.user.address['id'] != obj.project.address_id:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_storage_read_202')
            else:
                return Http403(error_code='iaas_storage_read_203')

        return None
