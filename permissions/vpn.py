# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import VPN
from iaas.utils import get_addresses_in_member

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.vpn methods
    """

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to update a VM is valid if:
        - The requesting user is public
        """
        # The requesting user is public
        if request.user.is_private:
            return Http403(error_code='iaas_vpn_create_201')
        return None

    @staticmethod
    def read(request: Request, obj: VPN, span: Span) -> Optional[Http403]:
        """
        The request to read a VPN is valid if;
        - The requesting User is the Robot from the region of the VPN of the Project.
        - The requesting User's Address owns the VPN.
        - The requesting User is global active and the VPN is owned by an address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.virtual_router.project.region_id:
                return Http403(error_code='iaas_vpn_read_201')

        elif obj.virtual_router.project.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.virtual_router.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_vpn_read_202')
            else:
                return Http403(error_code='iaas_vpn_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: VPN) -> Optional[Http403]:
        """
        The request to update a VPN is valid if:
        - The requesting User is the Robot from the region of the VPN of the Project.
        - The requesting User's Address owns the VPN
        - The requesting user is public
        """
        if request.user.robot:
            if request.user.address['id'] != obj.virtual_router.project.region_id:
                return Http403(error_code='iaas_vpn_update_201')
        elif request.user.address['id'] != obj.virtual_router.project.address_id:
            return Http403(error_code='iaas_vpn_update_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_vpn_update_203')

        return None

    @staticmethod
    def delete(request: Request, obj: VPN) -> Optional[Http403]:
        """
        The request to delete a VPN is valid if:
        - The requesting User is the Robot from the region of the VPN of the Project.
        - The requesting User's Address owns the VPN
        - The requesting user is public
        """
        if request.user.robot:
            if request.user.address['id'] != obj.virtual_router.project.region_id:
                return Http403(error_code='iaas_vpn_delete_201')
        elif request.user.address['id'] != obj.virtual_router.project.address_id:
            return Http403(error_code='iaas_vpn_delete_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_vpn_delete_203')

        return None
