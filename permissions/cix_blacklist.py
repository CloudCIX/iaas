# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a CIXBlacklist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_blacklist_create_201')

        return None

    @staticmethod
    def update(request):
        """
        The request to update a CIXBlacklist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_blacklist_update_201')

        return None

    @staticmethod
    def delete(request):
        """
        The request to delete a CIXBlacklist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_blacklist_delete_201')
