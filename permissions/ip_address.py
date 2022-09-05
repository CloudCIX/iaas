# python
from typing import Optional
# libs
# from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import (
    IPAddress,
    Project,
    Subnet,
)

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request, subnet: Subnet, cloud: bool) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - The User's Address owns the IPAddress' subnet.
        """
        if request.user.address['id'] not in {subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_create_201')

        return None

    @staticmethod
    def head(request: Request, obj: IPAddress, project: Optional[Project]) -> Optional[Http403]:
        """
        The request to access a IPAddress record is valid if:
        - The User's Address owns the Project that the IPAddress, if the IPAddress is related to the cloud.
        - The User's Address owns the IPAddress' Subnet, if not.
        """
        # Cloud Permission
        if project is not None:
            # Robot can read
            if request.user.robot:
                if request.user.address['id'] != project.region_id:
                    return Http403()
            # Cloud Owner can read
            elif request.user.address['id'] != project.address_id:
                return Http403()
        # Non-Cloud Permissions
        elif request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403()

        return None

    @staticmethod
    def read(request: Request, obj: IPAddress, project: Optional[Project]) -> Optional[Http403]:
        """
        The request to read a IPAddress record is valid if:
        - The User's Address owns the Project that the IPAddress, if the IPAddress is related to the cloud.
        - The User's Address owns the IPAddress' Subnet, if not.
        """
        # Cloud Permission
        if project is not None:
            # Robot can read
            if request.user.robot:
                if request.user.address['id'] != project.region_id:
                    return Http403(error_code='iaas_ip_address_read_201')
            # Cloud Owner can read
            elif request.user.address['id'] != project.address_id:
                return Http403(error_code='iaas_ip_address_read_202')
        # Non-Cloud Permissions
        elif request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_read_203')

        return None

    @staticmethod
    def update(request: Request, obj: IPAddress) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - The User's Address owns the IPAddress' Subnet, if not.
        - The IP Address is not a Cloud IP.
          configured on
        """
        if obj.cloud:
            return Http403(error_code='iaas_ip_address_update_201')

        # Non Cloud Permissions
        if request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_update_202')

        return None

    @staticmethod
    def delete(request: Request, obj: IPAddress) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - The User's Address owns the IPAddress' Subnet, if not.
        - It is not a Cloud IP Address
        """

        # Only robot users can delete can delete via the cloud resource it is configured on
        if obj.cloud:
            return Http403(error_code='iaas_ip_address_delete_201')

        # Non Cloud Permissions
        if request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_delete_202')

        return None
