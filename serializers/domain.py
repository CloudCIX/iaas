# libs
import serpy

__all__ = [
    'DomainSerializer',
]


class DomainSerializer(serpy.Serializer):
    """

    id:
        description: Rage4 ID of the Domain.
        type: integer
    created:
        description: Timestamp, in ISO format, of when the Domain record was created.
        type: string
    member_id:
        description: ID of the Member that owns the Domain.
        type: integer
    modified_by:
        description: ID of the User who last modified this Domain record.
        type: integer
    name:
        description: The domain name.
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Domain record was last updated.
        type: string
    uri:
        description: The absolute URL of the Domain record that can be used to perform `Read` and `Delete` methods.
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    member_id = serpy.Field()
    modified_by = serpy.Field()
    name = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
