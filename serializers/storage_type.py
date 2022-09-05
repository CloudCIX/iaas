# libs
import serpy

__all__ = [
    'StorageTypeSerializer',
]


class StorageTypeSerializer(serpy.Serializer):
    """
    created:
        description: The date that the Sever entry was created
        type: string
    id:
        description: The ID of the storage type.
        type: integer
    name:
        description: The name of the storage type.
        type: string
    regions:
        description: List of regions the storage type is available in.
        type: array
        items:
            type: integer
    updated:
        description: The date that the Server entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the storage type record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    name = serpy.Field()
    regions = serpy.Field(attr='get_regions', call=True)
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
