# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Router

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def list(request: Request) -> Optional[Http403]:
        """
        The request to list Routers is valid if:
        - User's address is a region
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        # User's address is a region
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_router_list_201')

        return None

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Router is valid if:
        - User's address is a region
        """
        # User's address is a region
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_router_create_201')

        return None

    @staticmethod
    def head(request: Request, router: Router) -> Optional[Http403]:
        """
        The request to access a Router is valid if:
        - Router's region is requesting users address
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        # Router's region is requesting users address
        if router.region_id != request.user.address['id']:
            return Http403()

        return None

    @staticmethod
    def read(request: Request, router: Router) -> Optional[Http403]:
        """
        The request to read a Router is valid if:
        - Router's region is requesting users address
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        # Router's region is requesting users address
        if router.region_id != request.user.address['id']:
            return Http403(error_code='iaas_router_read_201')

        return None

    @staticmethod
    def update(request: Request, router: Router) -> Optional[Http403]:
        """
        The request to update a Router is valid if:
        - Router's region is requesting users address
        """
        # Router's region is requesting users address
        if router.region_id != request.user.address['id']:
            return Http403(error_code='iaas_router_update_201')

        return None
