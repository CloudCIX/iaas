import serpy

__all__ = [
    'ServerTypeSerializer',
]


class ServerTypeSerializer(serpy.Serializer):
    """
    created:
        description: The date that the ServerType entry was created
        type: string
    id:
        description: ID for the ServerType
        type: integer
    name:
        description: Name of the ServerTypes
        type: string
    updated:
        description: The date that the ServerType entry was last updated
        type: string
    uri:
        description: The absolute URL of the ServerType that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    name = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(
        attr='get_absolute_url',
        call=True,
    )
