# libs
import serpy


__all__ = [
    'StorageHistorySerializer',
]


class StorageHistorySerializer(serpy.Serializer):
    """
    gb_quantity:
        description: The quantity of the GB for the Storage.
        type: integer
    gb_sku:
        description: The SKU for type of Storage for the Storage.
        type: string
    storage_id:
        description: The id for the Storage that has being changed.
        type: integer
    storage_name:
        description: The name of the storage which can be used for billing purposes
        type: string
    """

    gb_quantity = serpy.Field()
    gb_sku = serpy.Field()
    storage_id = serpy.Field()
    storage_name = serpy.Field()
