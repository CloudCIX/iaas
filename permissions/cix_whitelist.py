# python
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
        The request to create a CIXWhitelist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_whitelist_create_201')
        else:
            return None

    @staticmethod
    def update(request: Request) -> Optional[Http403]:
        """
        The request to update a CIXWhitelist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_whitelist_update_201')
        else:
            return None

    @staticmethod
    def delete(request: Request) -> Optional[Http403]:
        """
        The request to delete a CIXWhitelist record is valid if:
        - User is in Member 1
        """
        # The requesting User is in Member 1
        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_cix_whitelist_delete_201')
        else:
            return None
