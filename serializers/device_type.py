# libs
import serpy

__all__ = [
    'DeviceTypeSerializer',
]


class DeviceTypeSerializer(serpy.Serializer):
    """
    description:
        description: A human-readable description of the devices
        type: string
    id:
        description: The ID of the Device Type.
        type: integer
    sku:
        description: The SKU from SCM associated with this Device Type.
        type: string
    """
    description = serpy.Field()
    id = serpy.Field()
    sku = serpy.Field()
