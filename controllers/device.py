# stdlib
import re
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Device, DeviceType, Server

__all__ = [
    'DeviceListController',
    'DeviceCreateController',
    'DeviceUpdateController',
]

# Matches  XXXX:XX:XX.X where X is a lower-case hexadecimal digit
DEVICE_ID_PATTERN = r'^[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f]$'


class DeviceListController(ControllerBase):
    """
    Validates Device data used to filter a list of Device records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some Controller.Meta fields
        """
        max_list_limit = 100
        allowed_ordering = (
            'id_on_host',
            'created',
            'device_type_id'
            'id',
            'server_id',
            'updated',
            'vm_id',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id_on_host': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'device_type_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'device_type__description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'device_type__sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'server_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class DeviceCreateController(ControllerBase):
    """
    Validates Device data used to create a new Device
    """

    class Meta(ControllerBase.Meta):
        """
        Override some ControllerBase.Meta fields
        """
        model = Device
        validation_order = (
            'device_type_id',
            'id_on_host',
            'server_id',
        )

    def validate_device_type_id(self, device_type_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the DeviceType record that characterises the new Device
        type: integer
        """
        if device_type_id is None:
            return 'iaas_device_create_101'

        try:
            device_type_id = int(device_type_id)
        except (ValueError, TypeError):
            return 'iaas_device_create_102'

        try:
            obj = DeviceType.objects.get(pk=device_type_id)
        except DeviceType.DoesNotExist:
            return 'iaas_device_create_103'

        self.cleaned_data['device_type'] = obj
        return None

    def validate_id_on_host(self, id_on_host: Optional[str]) -> Optional[str]:
        """
        description: The ID that is used to identify the device on the Region host
        type: integer
        """
        if id_on_host is None:
            return 'iaas_device_create_104'

        id_on_host = str(id_on_host).lower()
        id_on_host.strip()

        match = re.fullmatch(DEVICE_ID_PATTERN, id_on_host)
        if match is None:
            return 'iaas_device_create_105'

        self.cleaned_data['id_on_host'] = id_on_host
        return None

    def validate_server_id(self, server_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the Server this Device is attached to
        type: integer
        """
        if server_id is None:
            return 'iaas_device_create_106'

        try:
            server_id = int(server_id)
        except (ValueError, TypeError):
            return 'iaas_device_create_107'

        try:
            obj = Server.objects.get(
                pk=server_id,
                region_id=self.request.user.address['id'],
            )
        except Server.DoesNotExist:
            return 'iaas_device_create_108'

        self.cleaned_data['server'] = obj
        return None


class DeviceUpdateController(ControllerBase):

    class Meta(ControllerBase.Meta):
        """
        Override some ControllerBase.Meta fields
        """
        model = Device
        validation_order = (
            'device_type_id',
            'id_on_host',
            'server_id',
            'vm_id',
        )

    def validate_device_type_id(self, device_type_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the DeviceType record that characterises the Device
        type: integer
        """
        if device_type_id is None:
            return 'iaas_device_update_101'

        try:
            device_type_id = int(device_type_id)
        except (ValueError, TypeError):
            return 'iaas_device_update_102'

        try:
            obj = DeviceType.objects.get(pk=device_type_id)
        except DeviceType.DoesNotExist:
            return 'iaas_device_update_103'

        self.cleaned_data['device_type'] = obj
        return None

    def validate_id_on_host(self, id_on_host: Optional[str]) -> Optional[str]:
        """
        description: The ID that is used to identify the device on the Server
        type: integer
        """
        if id_on_host is None:
            return 'iaas_device_update_104'

        id_on_host = str(id_on_host).lower()
        id_on_host.strip()

        match = re.fullmatch(DEVICE_ID_PATTERN, id_on_host)
        if match is None:
            return 'iaas_device_update_105'

        self.cleaned_data['id_on_host'] = id_on_host
        return None

    def validate_server_id(self, server_id: Optional[int]) -> Optional[str]:
        """
        description: ID of the Server this Device is attached to
        type: integer
        """
        if server_id is None:
            return 'iaas_device_update_106'

        try:
            server_id = int(server_id)
        except (ValueError, TypeError):
            return 'iaas_device_update_107'

        try:
            obj = Server.objects.get(
                pk=server_id,
                region_id=self.request.user.address['id'],
            )
        except Server.DoesNotExist:
            return 'iaas_device_update_108'

        self.cleaned_data['server'] = obj
        return None

    def validate_vm_id(self, vm_id: Optional[int]) -> Optional[str]:
        """
        description: The ID VM the Device is attached to
        required: False
        type: integer
        """
        # Robot is allowed to reset VM to None after detatching device
        if vm_id is None:
            self.cleaned_data['detach_device'] = True
        elif vm_id != self._instance.vm_id:
            return 'iaas_device_update_109'

        return None
