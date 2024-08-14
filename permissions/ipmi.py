# python
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import IPMI

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a IMPI record is valid if:
        - The requesting User is from Member 1.
        """

        if request.user.member['id'] != 1:
            return Http403(error_code='iaas_ipmi_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: IPMI) -> Optional[Http403]:
        """
        The request to read a IMPI record is valid if:
        - The requesting User is from Member 1.
        - The requesting User is from the Address that owns the Subnet that the IPMI customer_ip belongs to.
        """

        if request.user.member['id'] != 1 and obj.customer_ip.subnet.address_id != request.user.address['id']:
            return Http403(error_code='iaas_ipmi_read_201')
        return None

    @staticmethod
    def delete(request: Request, obj: IPMI) -> Optional[Http403]:
        """
        The request to delete a IMPI record is valid if:
        - The requesting User is from Member 1.
        - The requesting User is from the Address that owns the Subnet that the IPMI customer_ip belongs to.
        """

        if request.user.member['id'] != 1 and obj.customer_ip.subnet.address_id != request.user.address['id']:
            return Http403(error_code='iaas_ipmi_delete_201')

        return None
