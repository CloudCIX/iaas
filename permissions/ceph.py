# stdlib
from typing import Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import Resource

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.ceph methods
    """

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create Ceph is valid if:
        - The requesting user is public.
        """
        # The requesting user is public
        if request.user.is_private:
            return Http403(error_code='iaas_ceph_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: Resource, span: Span) -> Optional[Http403]:
        """
        The request to read Ceph is valid if;
        - The User is the API user
        - The User is the Robot for the Region where the Ceph's Project is set up
        - The requesting User's Address owns the Ceph
        - The requesting User is global active and the Ceph drive is owned by an Address in their Member
        """
        # The User is the API user
        if request.user.id == 1:
            return None

        # The User is the Robot for the Region where the Ceph's Project is set up
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_ceph_read_201')
            else:
                return None

        # The requesting User's Address owns the Ceph drive
        if obj.project.address_id == request.user.address['id']:
            return None

        # The requesting User is global active and the Ceph drive is owned by an Address in their Member
        if not request.user.global_active:
            return Http403(error_code='iaas_ceph_read_202')
        response = Membership.address.read(
            token=request.user.token,
            pk=obj.project.address_id,
            span=span,
        )
        ceph_member_id = -1
        if response.status_code == 200:
            ceph_member_id = response.json()['content']['member_id']
        if ceph_member_id != request.user.member['id']:
            return Http403(error_code='iaas_ceph_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: Resource) -> Optional[Http403]:
        """
        The request to update Ceph is valid if;
        - The Ceph drive is not attached to another Resource
        - The User is the Robot for the Region where the Ceph's Project is set up
        - The requesting User's Address owns the Ceph
        - The requesting user is public.
        """
        # The Ceph drive is not attached to another Resource
        if obj.parent_id is not None:
            return Http403(error_code='iaas_ceph_update_201')

        # The User is the Robot for the Region where the Ceph's Project is set up
        if request.user.robot:
            if request.user.address['id'] != obj.project.region_id:
                return Http403(error_code='iaas_ceph_update_202')
        # The requesting User's Address owns the Ceph drive
        elif obj.project.address_id != request.user.address['id']:
            return Http403(error_code='iaas_ceph_update_203')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_ceph_update_204')

        return None
