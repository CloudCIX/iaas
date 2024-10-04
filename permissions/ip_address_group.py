# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import IPAddressGroup

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request, obj: IPAddressGroup) -> Optional[Http403]:
        """
        The request to create an IP Address Group record is valid if:
        - The requesting User's Member is self-managed.
        - The reocrds member_id is 0 and the requesting users member_id is 1
        - The requesting Users member is the same as the records memner_id
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The requesting User's Member is self-managed.
        if not request.user.member['self_managed']:
            print(request.user.member['self_managed'])
            return Http403(error_code='iaas_ip_address_group_create_201')

        if obj.member_id != request.user.member_id:
            # The reocrds member_id is 0 and the requesting users member_id is 1
            if obj.member_id == 0 and request.user.member_id == 1:
                return None
            # The reocrds member_id is 0 and the requesting users member_id is 1
            return Http403(error_code='iaas_ip_address_group_create_202')

        return None

    @staticmethod
    def update(request: Request, obj: IPAddressGroup) -> Optional[Http403]:
        """
        The request to update an IP Address Group record is valid if:
        - The reocrds member_id is 0 and the requesting users member_id is 1
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The reocrds member_id is 0 and the requesting users member_id is 1
        if obj.member_id == 0 and request.user.member_id != 1:
            return Http403(error_code='iaas_ip_address_group_update_201')

        return None

    @staticmethod
    def delete(request: Request, obj: IPAddressGroup) -> Optional[Http403]:
        """
        The request to delete an IP Address Group record is valid if:
        - The reocrds member_id is 0 and the requesting users member_id is 1
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The reocrds member_id is 0 and the requesting users member_id is 1
        if obj.member_id == 0 and request.user.member_id != 1:
            return Http403(error_code='iaas_ip_address_group_delete_201')

        # TODO: Extend permissions when group can be source/destination in a firewall rule
        return None
