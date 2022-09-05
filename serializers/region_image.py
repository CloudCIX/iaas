# libs
import serpy  # pragma: no cover


class RegionImageSerializer(serpy.Serializer):  # pragma: no cover
    """
    region_image:
        description: Dummy Serializer
        type: string
    """
    region_image = serpy.Field()
