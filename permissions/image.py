# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Image

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def update(request: Request, obj: Image) -> Optional[Http403]:
        """
        The request to update an image is allowed if:
        - The requesting User is an Administrator from address 1.
        """
        if (not request.user.address['id'] == 1 and not
                request.user.administrator):
            return Http403(error_code='iaas_image_update_201')

        return None
