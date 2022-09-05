# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Record

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Record is valid if:
        - The requesting User's Member is self managed.
        """
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_ptr_record_create_201')
        return None

    @staticmethod
    def update(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to update a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """
        if request.user.member['id'] not in {1, record.member_id}:
            return Http403(error_code='iaas_ptr_record_update_201')

        return None

    @staticmethod
    def delete(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to delete a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """
        if request.user.member['id'] not in {1, record.member_id}:
            return Http403(error_code='iaas_ptr_record_delete_201')

        return None
