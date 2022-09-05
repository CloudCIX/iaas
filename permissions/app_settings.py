# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create App Settings is valid if:
        - User is a super user
        """
        # Requesting user is not a super user
        if request.user.id != 1:
            return Http403(error_code='iaas_app_settings_create_201')

        return None

    @staticmethod
    def read(request: Request) -> Optional[Http403]:
        """
        The request to read App Settings is valid if:
        - User is a super user
        """
        # Requesting user is not a super user
        if request.user.id != 1:
            return Http403(error_code='iaas_app_settings_read_201')

        return None

    @staticmethod
    def update(request: Request) -> Optional[Http403]:
        """
        The request to update App Settings is valid if:
        - User is a super user
        """
        # Requesting user is not a super user
        if request.user.id != 1:
            return Http403(error_code='iaas_app_settings_update_201')

        return None

    @staticmethod
    def delete(request: Request) -> Optional[Http403]:
        """
        The request to delete App Settings is valid if:
        - User is a super user
        """
        # Requesting user is not a super user
        if request.user.id != 1:
            return Http403(error_code='iaas_app_settings_delete_201')

        return None
