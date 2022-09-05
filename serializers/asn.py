# libs
import serpy

__all__ = [
    'ASNSerializer',
]


class ASNSerializer(serpy.Serializer):
    """
    allocations_in_use:
        description: The total number of Allocations that are in use in this ASN
        type: integer
    created:
        description: Timestamp, in ISO format, of when the ASN record was created.
        type: string
    id:
        description: The ID of the ASN record
        type: integer
    member_id:
        description: The id of the Member that owns the ASN record
        type: integer
    number:
        description: The number of the ASN record
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the ASN record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the ASN record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    allocations_in_use = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    member_id = serpy.Field()
    number = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
