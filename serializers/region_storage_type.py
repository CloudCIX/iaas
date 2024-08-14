# libs
import serpy  # pragma: no cover


class RegionStorageTypeSerializer(serpy.Serializer):  # pragma: no cover
    """
    region_storage_type:
        description: Dummy Serializer
        type: string
    """
    region_storage_type = serpy.Field()
