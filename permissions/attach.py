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
    def update(request: Request) -> Optional[Http403]:
        """
        The request to attach Resources is valid if:
        - The requesting user is not a robot
        - The requesting user is public.
        """
        if request.user.robot:
            return Http403(error_code='iaas_attach_update_201')
        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_attach_update_202')

        return None
