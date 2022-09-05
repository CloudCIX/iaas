# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Allocation

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create an Allocation record is valid if:
        - User is administrator
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The requesting User is Administrator
        if not request.user.administrator:
            return Http403(error_code='iaas_allocation_create_201')

        # The requesting User is from a self-managed Member
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_allocation_create_202')

        return None

    @staticmethod
    def head(request: Request, allocation: Allocation) -> Optional[Http403]:
        """
        The request to access an Allocation record is valid if:
        - The User's Member owns the ASN that the Allocation is in, or
        - The User's Address owns the Allocation record.
        """
        if request.user.address['id'] == 1:
            return None

        if request.user.member['id'] != allocation.asn.member_id:
            if request.user.address['id'] != allocation.address_id:
                return Http403()

        return None

    @staticmethod
    def read(request: Request, allocation: Allocation) -> Optional[Http403]:
        """
        The request to read an Allocation record is valid if:
        - The User's Member owns the ASN that the Allocation is in, or
        - The User's Address owns the Allocation record.
        """
        if request.user.address['id'] == 1:
            return None

        if request.user.member['id'] != allocation.asn.member_id:
            if request.user.address['id'] != allocation.address_id:
                return Http403(error_code='iaas_allocation_read_201')

        return None

    @staticmethod
    def update(request: Request, allocation: Allocation) -> Optional[Http403]:
        """
        The request to update an Allocation record is valid if:
        - User is administrator
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        if not request.user.administrator:
            return Http403(error_code='iaas_allocation_update_201')

        # The requesting User is from a self-managed Member
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_allocation_update_202')

        if request.user.address['id'] != 1 and allocation.asn.member_id != request.user.member['id']:
            return Http403(error_code='iaas_allocation_update_203')

        return None

    @staticmethod
    def delete(request: Request, allocation: Allocation) -> Optional[Http403]:
        """
        The request to delete an Allocation record is valid if:
        - User is administrator
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        if not request.user.administrator:
            return Http403(error_code='iaas_allocation_delete_201')

        # The requesting User is from a self-managed Member
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_allocation_delete_202')

        if request.user.address['id'] != 1 and allocation.asn.member_id != request.user.member['id']:
            return Http403(error_code='iaas_allocation_delete_203')

        return None
