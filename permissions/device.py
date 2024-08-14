# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Device


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Device record is valid if:
        - The requesting user is an administrator in a cloud region
        """
        # Requesting user is an administrator in a cloud region
        if not request.user.administrator or not request.user.address['cloud_region']:
            return Http403(error_code='iaas_device_create_201')

        return None

    @staticmethod
    def read(request: Request, device: Device) -> Optional[Http403]:
        """
        The request to read a Device is valid if:
        - Device's server region is requesting users address
        """
        if request.user.id == 1:  # pragma: no cover
            return None
        if device.server.region_id != request.user.address['id']:
            return Http403(error_code='iaas_device_read_201')

        return None

    @staticmethod
    def update(request: Request, device: Device) -> Optional[Http403]:
        """
        The request to update a Device is valid if:
        - Device is not connected to a VM or the user is robot
        """
        # Robot can update device to set vm to null
        if device.vm is not None:
            if not request.user.robot:
                return Http403(error_code='iaas_device_update_201')

        return None
