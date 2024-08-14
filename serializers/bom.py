# libs
import serpy

__all__ = [
    'BOMSerializer',
]


class BOMSerializer(serpy.Serializer):
    """
    sku:
        description: An identifier for a billable entity that a Resource utilises
        type: string
    quantity:
        description: How many units of a billable entity that a Resource utilises
        type: integer
    """
    sku = serpy.Field()
    quantity = serpy.Field()
