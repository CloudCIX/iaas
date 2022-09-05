# libs
import serpy
# local
from .ip_address import IPAddressSerializer
from .pool_ip import PoolIPSerializer

__all__ = [
    'IPMISerializer',
]


class IPMISerializer(serpy.Serializer):
    """
    client_ip:
        description: The IP address that the client will be using to connect to the IPMI url.
        type: string
    created:
        description: Timestamp, in ISO format, of when the IPMI record was created.
        type: string
    customer_ip:
        $ref: '#/components/schemas/IPAddress'
    id:
        description: The ID of the IPMI record
        type: integer
    in_use:
        description: A flag currently stating whether or not the IPMI record is currently in use.
        type: boolean
    modified_by:
        description: The ID of the User who last made changes to this IPMI record
        type: integer
    pool_ip:
        $ref: '#/components/schemas/PoolIP'
    removed:
        description: |
            A timestamp in ISO format indicating the date and time at which the IPMI record was removed from
            the CIX routers and made inactive.
        type: string
    updated:
        description: Timestamp, in ISO format, of when the IPMI record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the IPMI record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    client_ip = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    customer_ip = IPAddressSerializer()
    id = serpy.Field()
    in_use = serpy.Field()
    modified_by = serpy.Field()
    pool_ip = PoolIPSerializer()
    removed = serpy.Field(attr='removed.isoformat', call=True, required=False)
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
