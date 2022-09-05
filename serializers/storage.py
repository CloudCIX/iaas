import serpy

__all__ = [
    'StorageSerializer',
]


class StorageSerializer(serpy.Serializer):
    """
    created:
        description: The date that the Sever entry was created
        type: string
    gb:
        description: Storage size in GBs
        type: integer
    history:
        description:
        $ref: '#/components/schemas/StorageHistory'
    id:
        description: ID of the Storage record
        type: integer
    name:
        description: Name of the device
        type: string
    primary:
        description: If the storage is the primary storage of the device or not
        type: boolean
    updated:
        description: The date that the Server entry was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the Storage instance
        type: string
        format: url
    vm_id:
        description: ID of the vm of the storage device
        type: integer
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    gb = serpy.Field()
    history = serpy.Field(attr='get_history', call=True)
    id = serpy.Field()
    name = serpy.Field()
    primary = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    vm_id = serpy.Field()
