# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Interface

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def list(request: Request) -> Optional[Http403]:
        """
        The request to list Interfaces is allowed if:
        - The requesting User's address is a region
        """
        if request.user.address['id'] == 1:  # pragma: no cover
            return None
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_interface_list_201')
        return None

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create an interface is allowed if:
        - The requesting User's address is a region
        """
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_interface_create_201')
        return None

    @staticmethod
    def head(request: Request, obj: Interface) -> Optional[Http403]:
        """
        The request to access an interface is valid if:
       - Interface's server's region is requesting users address
        """
        if request.user.address['id'] == 1:  # pragma: no cover
            return None
        if obj.server.region_id != request.user.address['id']:
            return Http403()
        return None

    @staticmethod
    def read(request: Request, obj: Interface) -> Optional[Http403]:
        """
        The request to get an interface is valid if:
        - Interface's server's region is requesting users address
        """
        if request.user.address['id'] == 1:  # pragma: no cover
            return None
        if obj.server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_interface_read_201')
        return None

    @staticmethod
    def update(request: Request, obj: Interface) -> Optional[Http403]:
        """
        The request to update an interface is allowed if:
        - Interface's server's region is requesting users address
        """
        if obj.server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_interface_update_201')
        return None

    @staticmethod
    def delete(request: Request, obj: Interface) -> Optional[Http403]:
        """
        The request to delete an interface is allowed if:
        - Interface's server's region is requesting users address
        """
        if obj.server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_interface_delete_201')
        return None
