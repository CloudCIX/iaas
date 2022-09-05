# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import VirtualRouter
from iaas.utils import get_addresses_in_member


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def head(request: Request, obj: VirtualRouter, span: Span) -> Optional[Http403]:
        """
        The request to access a VirtualRouter is valid if:
        - The requesting User is the Robot from the region that the Project is in.
        - The requesting User owns the Project that the VirtualRouter is associated with.
        - The requesting User is global active and the Project that the VirtualRouter is associated with is owned by an
          address in their Member.
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
    def read(request: Request, obj: VirtualRouter, span: Span) -> Optional[Http403]:
        """
        The request to get a VirtualRouter is valid if:
        - The requesting User is the Robot from the region that the Project is in.
        - The requesting User owns the Project that the VirtualRouter is associated with.
        - The requesting User is global active and the Project that the VirtualRouter is associated with is owned by an
          address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_virtual_router_read_201')
        elif obj.project.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.project.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_virtual_router_read_202')
            else:
                return Http403(error_code='iaas_virtual_router_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: VirtualRouter) -> Optional[Http403]:
        """
        The request to get a VirtualRouter is valid if:
        - The requesting User is the Robot from the region that the Project is in.
        - The requesting User owns the Project that the VirtualRouter is associated with.
        """
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_virtual_router_update_201')
        else:
            if request.user.address['id'] != obj.project.address_id:
                return Http403(error_code='iaas_virtual_router_update_202')
        return None
