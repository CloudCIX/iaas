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
    def list(request: Request) -> Optional[Http403]:
        """
        The request to verify run_robot is valid if:
        - User is robot
        """
        if not request.user.robot:
            return Http403(error_code='iaas_run_robot_list_201')

        return None

    @staticmethod
    def turn_off(request: Request) -> Optional[Http403]:
        """
        The request to turn off run_robot is valid if:
        - User is robot
        """
        if not request.user.robot:
            return Http403(error_code='iaas_run_robot_turn_off_201')
        return None
