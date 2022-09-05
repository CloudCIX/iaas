# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Domain

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
            return Http403(error_code='iaas_domain_create_201')
        return None

    @staticmethod
    def head(request: Request, domain: Domain) -> Optional[Http403]:
        """
        The request to access a Domain record is valid if:
        - The Domain is owned by the User's Member.
        """
        if request.user.member['id'] not in [1, domain.member_id]:
            return Http403()

        return None

    @staticmethod
    def read(request: Request, domain: Domain) -> Optional[Http403]:
        """
        The request to read a Domain record is valid if:
        - The Domain is owned by the User's Member.
        """
        if request.user.member['id'] not in [1, domain.member_id]:
            return Http403(error_code='iaas_domain_read_201')

        return None

    @staticmethod
    def delete(request: Request, domain: Domain) -> Optional[Http403]:
        """
        The request to delete a Domain record is valid if:
        - The Domain is owned by the User's Member.
        """
        if request.user.member['id'] not in [1, domain.member_id]:
            return Http403(error_code='iaas_domain_delete_201')

        return None
