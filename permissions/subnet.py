# stdlib
from typing import Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.models import Subnet, VirtualRouter

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def head(request: Request, subnet: Subnet, span: Span) -> Optional[Http403]:
        """
        The request to access a Subnet record is valid if:
        - The requesting User's Address owns the Subnet.
        - The requesting User's Address owns the parent Subnet of the Subnet.
        - The requesting User's Address owns the Allocation of the Subnet.
        - The Subnet is owned by an Address that is linked to the User's Address, and is in a non self managed Member.
        - The Subnet is related to a cloud Project owned by the requesting User's Address.
        """
        # API User allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # If the Subnet is for the Cloud, handle things a little differently
        if subnet.cloud:
            # If the request is coming from Robot  ensure they can read it
            if request.user.robot:
                virtual_router = VirtualRouter.objects.get(pk=subnet.virtual_router_id)
                # If the User is not global, ensure that the Project is in the same region.
                if virtual_router.project.region_id != request.user.address['id']:
                    return Http403()
            else:
                # Ensure that the Subnet is owned by the requesting User ID
                if request.user.address['id'] != subnet.address_id:
                    # If user is global and Subnet is from their Member, they need to change address
                    if request.user.is_global and request.user.member['id'] == subnet.allocation.asn.member_id:
                        return Http403()
                    return Http403()

        # If not, check the other permissions
        else:
            obj_addresses = {
                subnet.address_id,
                subnet.parent.address_id if subnet.parent is not None else -1,
                subnet.allocation.address_id,
            }
            if request.user.address['id'] not in obj_addresses:
                # Check that the Subnet is owned by a linked Address by attempting to read the Address that owns it.
                response = Membership.address.read(
                    token=request.auth,
                    pk=subnet.address_id,
                    span=span,
                )
                if response.status_code != 200:
                    return Http403()
                if response.json()['content']['member']['self_managed']:
                    return Http403()
        return None

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Subnet record is valid if:
        - The requesting User's Member is self managed.
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The requesting User is self_managed
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_subnet_create_201')

        return None

    @staticmethod
    def read(request: Request, subnet: Subnet, span: Span) -> Optional[Http403]:
        """
        The request to read a Subnet record is valid if:
        - The requesting User's Address owns the Subnet.
        - The requesting User's Address owns the parent Subnet of the Subnet.
        - The requesting User's Address owns the Allocation of the Subnet.
        - The Subnet is owned by an Address that is linked to the User's Address, and is in a non self managed Member.
        - The Subnet is related to a cloud Project owned by the requesting User's Address.
        """
        # API User allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # If the Subnet is for the Cloud, handle things a little differently
        if subnet.cloud:
            # If the request is coming from Robot, ensure they can read it
            if request.user.robot:
                virtual_router = VirtualRouter.objects.get(pk=subnet.virtual_router_id)
                # ensure that the Project is in the same region.
                if virtual_router.project.region_id != request.user.address['id']:
                    return Http403(error_code='iaas_subnet_read_201')
            else:
                # Ensure that the Subnet is owned by the requesting User ID
                if request.user.address['id'] != subnet.address_id:
                    # If user is global and Subnet is from their Member, they need to change address
                    if request.user.is_global and request.user.member['id'] == subnet.allocation.asn.member_id:
                        return Http403(error_code='iaas_subnet_read_202')
                    return Http403(error_code='iaas_subnet_read_203')

        # If not, check the other permissions
        else:
            obj_addresses = {
                subnet.address_id,
                subnet.parent.address_id if subnet.parent is not None else -1,
                subnet.allocation.address_id,
            }
            if request.user.address['id'] not in obj_addresses:
                # Check that the Subnet is owned by a linked Address by attempting to read the Address that owns it.
                response = Membership.address.read(
                    token=request.auth,
                    pk=subnet.address_id,
                    span=span,
                )
                if response.status_code != 200:
                    return Http403(error_code='iaas_subnet_read_204')
                if response.json()['content']['member']['self_managed']:
                    return Http403(error_code='iaas_subnet_read_205')
        return None

    @staticmethod
    def update(request: Request, subnet: Subnet, span: Span) -> Optional[Http403]:
        """
        The request to update a Subnet record is valid if:
        - The requesting User's Member is self managed, and;
        - The requesting User's Address owns the Subnet.
        - The requesting User's Address owns the parent Subnet of the Subnet.
        - The requesting User's Address owns the Allocation of the Subnet.
        - The Subnet is owned by an Address that is linked to the User's Address, and is in a non self managed
          Member.
        - The Subnet is not related to a cloud Project.
        """
        # API User allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # Ensure the User is from a self managed Member
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_subnet_update_201')

        # If it is a cloud subnet it can only be updated when updating the virtual router it is associated with
        if subnet.cloud:
            return Http403(error_code='iaas_subnet_update_202')

        obj_addresses = {
            subnet.address_id,
            subnet.parent.address_id if subnet.parent is not None else -1,
            subnet.allocation.address_id,
        }
        if request.user.address['id'] not in obj_addresses:
            # Check that the Subnet is owned by a linked Address by attempting to read the Address that owns it.
            response = Membership.address.read(
                token=request.auth,
                pk=subnet.address_id,
                span=span,
            )
            if response.status_code != 200:
                return Http403(error_code='iaas_subnet_update_203')
            if response.json()['content']['member']['self_managed']:
                return Http403(error_code='iaas_subnet_update_204')

        return None

    @staticmethod
    def delete(request: Request, subnet: Subnet, span: Span) -> Optional[Http403]:
        """
        The request to delete a Subnet record is valid if:
        - The requesting User's Member is self managed, and
        - The chosen Subnet has no children Subnets, and;
        - The requesting User's Address owns the Subnet.
        - The requesting User's Address owns the parent Subnet of the Subnet.
        - The requesting User's Address owns the Allocation of the Subnet.
        - The Subnet is owned by an Address that is linked to the User's Address, and is in a non self managed
          Member.
        """
        # API User allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # Ensure the User is from a self managed Member
        if not request.user.member['self_managed']:
            return Http403(error_code='iaas_subnet_delete_201')

        if subnet.children.exists():
            return Http403(error_code='iaas_subnet_delete_202')

        # If it is a cloud subnet it can only be deleted when deleting the virtual router it is associated with
        if subnet.cloud:
            return Http403(error_code='iaas_subnet_delete_203')

        # If not, check the other permissions
        else:
            obj_addresses = {
                subnet.address_id,
                subnet.parent.address_id if subnet.parent is not None else -1,
                subnet.allocation.address_id,
            }
            if request.user.address['id'] not in obj_addresses:
                # Check that the Subnet is owned by a linked Address by attempting to read the Address that owns it.
                response = Membership.address.read(
                    token=request.auth,
                    pk=subnet.address_id,
                    span=span,
                )
                if response.status_code != 200:
                    return Http403(error_code='iaas_subnet_delete_204')
                if response.json()['content']['member']['self_managed']:
                    return Http403(error_code='iaas_subnet_delete_205')
        return None
