# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Resource

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def update(request: Request, obj: Resource) -> Optional[Http403]:
        """
        The request to detach Resources is valid if:
        - The requesting user is a robot and the object is in the robot's region
        - The requesting user is public.
        """
        if request.user.robot:
            if obj.project.region_id != request.user.address_id:
                return Http403(error_code='iaas_detach_update_201')

        # The requesting user is public
        elif request.user.is_private:
            return Http403(error_code='iaas_detach_update_202')
        return None
