# libs
import serpy

__all__ = [
    'PoolIPSerializer',
]


class PoolIPSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the PoolIP record was created.
        type: string
    domain:
        description: The domain name Users can use to connect to the IP address in the OOB.
        type: string
    id:
        description: The ID of the PoolIP record.
        type: integer
    ip_address:
        description: The OOB IP address that this PoolIP record represents.
        type: string
    modified_by:
        description: The ID of the User who last made changes to this PoolIP record.
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the PoolIP record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the PoolIP record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    domain = serpy.Field()
    id = serpy.Field()
    ip_address = serpy.Field()
    modified_by = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
