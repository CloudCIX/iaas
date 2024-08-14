# libs
import serpy
# local
from .device_type import DeviceTypeSerializer
from .server import ServerSerializer

__all__ = [
    'DeviceSerializer',
]


class DeviceSerializer(serpy.Serializer):
    """
    device_type:
        $ref: '#/components/schemas/DeviceType'
    device_type_id:
        description: The id of the Device Type of this device.
        type: integer
    id:
        description: The ID of the Device.
        type: integer
    id_on_host:
        description: The identifier of the device on the Region host.
        type: string
    server:
        $ref: '#/components/schemas/Server'
    server_id:
        description: The id of the Server this device is attached to.
        type: integer
    vm_id:
        description: The id of the VM this device is attached to.
        type: integer
    """
    device_type = DeviceTypeSerializer()
    device_type_id = serpy.Field()
    id = serpy.Field()
    id_on_host = serpy.Field()
    server = ServerSerializer()
    server_id = serpy.Field()
    vm_id = serpy.Field()
