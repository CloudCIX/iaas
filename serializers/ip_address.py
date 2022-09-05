# libs
import serpy
# local
from .subnet import SubnetSerializer

__all__ = [
    'NATIPAddressSerializer',
    'IPAddressSerializer',
]


class NATIPAddressSerializer(serpy.Serializer):
    """
    address:
        description: The actual address of the Public IPAddress record.
        type: string
    id:
        description: The ID of the Public IPAddress record.
        type: integer
    """
    address = serpy.Field()
    id = serpy.Field()


class IPAddressSerializer(NATIPAddressSerializer):
    """
    address:
        description: The actual address of the IPAddress record.
        type: string
    cloud:
        description: A flag stating whether or not the IPAddress record is related to the Cloud operations.
        type: boolean
    created:
        description: Timestamp, in ISO format, of when the IPAddress record was created.
        type: string
    credentials:
        description: An optional string containing credentials information for the IPAddress record.
        type: string
    id:
        description: The ID of the IPAddress record.
        type: integer
    location:
        description: An optional string containing location information for the IPAddress record.
        type: string
    modified_by:
        description: ID of the User who last updated this IPAddress record.
        type: integer
    name:
        description: A verbose name given to the IPAddress record.
        type: string
    public_ip:
        $ref: '#/components/schemas/NATIPAddress'
    subnet:
        $ref: '#/components/schemas/Subnet'
    updated:
        description: Timestamp, in ISO format, of when the IPAddress record was last updated.
        type: string
    vm_id:
        description: The ID of the VM the IP Address is configured on.
        type: integer
    """
    cloud = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    credentials = serpy.Field()
    location = serpy.Field()
    modified_by = serpy.Field()
    name = serpy.Field()
    public_ip = NATIPAddressSerializer(required=False)
    subnet = SubnetSerializer()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    vm_id = serpy.Field()
