# libs
import serpy
# local
from .subnet import SubnetSerializer

__all__ = [
    'RouteSerializer',
]


class RouteSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the Route record was created.
        type: string
    id:
        description: The ID of the Route record
        type: integer
    local_subnet:
        $ref: '#/components/schemas/Subnet'
    remote_subnet:
        description: A subnet from the customer's side that is allowed through the VPN to the local subnet.
        type: string
    updated:
        description: Timestamp, in ISO format, of when the Route record was last updated.
        type: string
    """

    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    local_subnet = SubnetSerializer()
    remote_subnet = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
