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
    def head(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to access a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """
        if request.user.member['id'] not in {1, record.domain.member_id}:
            return Http403()

        return None

    @staticmethod
    def read(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to read a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """
        if request.user.member['id'] not in {1, record.domain.member_id}:
            return Http403(error_code='iaas_record_read_201')

        return None

    @staticmethod
    def update(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to update a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """
        if request.user.member['id'] not in {1, record.domain.member_id}:
            return Http403(error_code='iaas_record_update_201')

        return None

    @staticmethod
    def delete(request: Request, record: Record) -> Optional[Http403]:
        """
        The request to delete a Record record is valid if:
        - The requesting User is in the Member that owns the Record.
        """

        if request.user.member['id'] not in {1, record.domain.member_id}:
            return Http403(error_code='iaas_record_delete_201')

        return None
