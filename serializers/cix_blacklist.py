# libs
import serpy

__all__ = [
    'CIXBlacklistSerializer',
]


class CIXBlacklistSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the CIDR was first added to the Blacklist.
        type: string
    cidr:
        description: The CIDR being blocked.
        type: string
    comment:
        description: The comment about the CIDR being blocked.
        type: string
    modified_by:
        description: The ID of the User that updated the record last.
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the CIDR was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the CIXBlacklist record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    cidr = serpy.Field()
    comment = serpy.Field()
    modified_by = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
