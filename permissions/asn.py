# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import ASN

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request, number: int) -> Optional[Http403]:
        """
        The request to create a ASN record is valid if:
        - The User is in Address 1.
        - It is a Pseudo ASN and the User owns the corresponding Project
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The requesting User is in Address 1
        if number < ASN.pseudo_asn_offset and request.user.address['id'] != 1:
            return Http403(error_code='iaas_asn_create_201')

        # It is a Pseudo ASN
        if number >= ASN.pseudo_asn_offset:
            return Http403(error_code='iaas_asn_create_202')

        return None

    @staticmethod
    def update(request: Request, asn: ASN) -> Optional[Http403]:
        """
        The request to update a ASN record is valid if:
        - The User is in Address 1.
        - The ASN being updated is not a pseudo ASN.
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        if request.user.address['id'] != 1:
            return Http403(error_code='iaas_asn_update_201')

        # pseudoASNs (number of 1 trillion)
        if asn.is_pseudo:
            return Http403(error_code='iaas_asn_update_202')

        return None

    @staticmethod
    def delete(request: Request, asn: ASN) -> Optional[Http403]:
        """
        The request to delete a ASN record is valid if:
        - The User is in Address 1.
        - If the ASN is pseudo, the corresponding Project must exist, and the requesting User must be the correct Robot.
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # pseudoASNs (number of 1 trillion)
        if asn.is_pseudo:
            return Http403(error_code='iaas_asn_delete_201')
        elif request.user.address['id'] != 1:
            return Http403(error_code='iaas_asn_delete_202')

        return None
