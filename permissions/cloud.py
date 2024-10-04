# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import Project
from iaas.utils import get_addresses_in_member


__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.Cloud methods
    """

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to use this method is valid if;
        - The requesting User's Member is self managed.
        - The requesting user is public.
        """
        if request.user.robot:
            return Http403(error_code='iaas_cloud_create_201')
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_cloud_create_202')
        # The requesting user is public
        if request.user.is_private:
            return Http403(error_code='iaas_cloud_create_203')

        return None

    @staticmethod
    def read(request: Request, obj: Project, span: Span) -> Optional[Http403]:
        """
        The request to use this method is valid if;
        - The requesting User's Address owns the Project.
        - The requesting user is global active and the Project belongs to an Address in their Member.
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if obj.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_cloud_read_201')
            else:
                return Http403(error_code='iaas_cloud_read_202')

        return None

    @staticmethod
    def update(request: Request, obj: Project) -> Optional[Http403]:
        """
        The request to use this method is valid if;
        - The requesting User's Address owns the Project.
        - The requesting user is public.
        """
        if request.user.robot:
            return Http403(error_code='iaas_cloud_update_201')
        elif obj.address_id != request.user.address['id']:
            return Http403(error_code='iaas_cloud_update_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_cloud_update_203')

        return None
