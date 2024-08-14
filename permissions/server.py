# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Server

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def list(request: Request) -> Optional[Http403]:
        """
        The request to list Servers is valid if:
        - User's address is a region
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        # Requesting user is robot
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_server_list_201')

        return None

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create Servers is valid if:
        - User's address is a region
        """
        # Requesting user is robot
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_server_create_201')

        return None

    @staticmethod
    def read(request: Request, server: Server) -> Optional[Http403]:
        """
        The request to read a Server is valid if:
        - Server's region is requesting users address
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_server_read_201')

        return None

    @staticmethod
    def update(request: Request, server: Server) -> Optional[Http403]:
        """
        The request to update a Server is valid if:
        - Server's region is requesting users address
        """
        if server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_server_update_201')

        return None
