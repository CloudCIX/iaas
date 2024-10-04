# libs
import serpy

__all__ = [
    'IPAddressGroupSerializer',
]


class IPAddressGroupSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the IP Address Group was created.
        type: string
    cidrs:
        description: An array of CIDR addresses in the IP Address Group.
        type: array
        items:
            type: string
    id:
        description: The ID of the IP Address Goup record
        type: integer
    member_id:
        description: The ID of the Member that owns the IP Address Group record
        type: integer
    name:
        description: The name of the IP Address Group.
        type: string
    updated:
        description: Timestamp, in ISO format, of when the IP Address Group was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the IP Address Group record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    version:
        description: The IP Version of the CIDRs in the group.
        type: integer
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    cidrs = serpy.Field()
    id = serpy.Field()
    member_id = serpy.Field()
    name = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    version = serpy.Field()
