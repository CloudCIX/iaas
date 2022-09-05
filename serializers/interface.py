# libs
import serpy

__all__ = [
    'InterfaceSerializer',
]


class InterfaceSerializer(serpy.Serializer):
    """
    created:
        description: The date that the Interface entry was created
        type: string
    details:
        description: Details of the Interface.
        type: string
    enabled:
        description: Flag indicating whether the Interface is enabled.
        type: boolean
    hostname:
        description: The hostname of the Interface.
        type: string
    id:
        description: The ID of the Interface.
        type: integer
    ip_address:
        description: The IP address of the interface.
        type: string
    mac_address:
        description: The MAC address of the Interface.
        type: string
    server_id:
        description: The ID of the server on which this Interface is.
        type: integer
    updated:
        description: The date that the Interface entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the Interface record that can be used to perform `Read`, `Update` and `Delete`
        type: string

    """
    created = serpy.Field(attr='created.isoformat', call=True)
    details = serpy.Field()
    enabled = serpy.Field()
    hostname = serpy.Field()
    id = serpy.Field()
    ip_address = serpy.Field()
    mac_address = serpy.Field()
    server_id = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
