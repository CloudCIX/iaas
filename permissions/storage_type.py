# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import StorageType

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def update(request: Request, obj: StorageType) -> Optional[Http403]:
        """
        The request to update a storage type is allowed if:
        - - The requesting User is an Administrator from address 1.
        """
        if (not request.user.address['id'] == 1 and not
                request.user.administrator):
            return Http403(error_code='iaas_storage_type_update_201')

        return None
