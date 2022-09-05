# python
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def read(request: Request, region_id: int) -> Optional[Http403]:
        """
        The request for metrics is valid if;
        - The user is the PAM user
        """
        if request.user.id == 1:
            return None

        return Http403(error_code='iaas_metrics_read_201')
