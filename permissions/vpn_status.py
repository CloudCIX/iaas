# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import VPN

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.VPN methods
    """

    @staticmethod
    def read(request: Request, obj: VPN) -> Optional[Http403]:
        """
        The request to read VPN status for a VPN is valid if;
        - The requesting User owns to chosen VPN.
        """
        if obj.virtual_router.project.address_id != request.user.address['id']:
            return Http403(error_code='iaas_vpn_status_read_201')

        return None
