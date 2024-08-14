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
    Checks the permissions of the views.Project methods
    """

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Project is valid if;
        - The requesting User is self managed.
        - The requesting user is public.
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_project_create_201')
        # The requesting user is public
        if request.user.is_private:
            return Http403(error_code='iaas_project_create_202')

        return None

    @staticmethod
    def read(request: Request, obj: Project, span: Span) -> Optional[Http403]:
        """
        The request to read a Project is valid if;
        - The requesting User is a Robot from the same region as the Project in question.
        - The requesting User's Address owns the Project.
        - The requesting user is global active and Project is owned by an address in their Member.
        """
        if request.user.address['id'] == 1:  # pragma: no cover
            return None
        if request.user.robot:
            if obj.region_id != request.user.address['id']:
                return Http403(error_code='iaas_project_read_201')
        elif obj.address_id != request.user.address['id']:
            if request.user.is_global and request.user.global_active:
                if obj.address_id not in get_addresses_in_member(request, span):
                    return Http403(error_code='iaas_project_read_202')
            else:
                return Http403(error_code='iaas_project_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: Project) -> Optional[Http403]:
        """
        The request to update a Project is valid if;
        - The requesting User is a Robot from the same region as the Project in question.
        - The requesting User's Address owns the Project.
        - The requesting user is public.
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if request.user.robot:
            if obj.region_id != request.user.address['id']:
                return Http403(error_code='iaas_project_update_201')
        elif obj.address_id != request.user.address['id']:
            return Http403(error_code='iaas_project_update_202')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_project_update_203')

        return None
