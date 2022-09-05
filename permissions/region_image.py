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
        The request to create an RegionImage record is valid if:
        - User's address is a cloud region
        """
        # The requesting User's Address is a cloud region
        if not request.user.address['cloud_region']:
            return Http403(error_code='iaas_region_image_create_201')

        return None
