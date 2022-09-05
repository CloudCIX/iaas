# libs
import serpy
# local
from .allocation import AllocationSerializer

__all__ = [
    'RelatedSubnetSerializer',
    'SubnetSerializer',
    'SubnetSpaceSerializer',
]


# Serializer specific for related subnets, don't include parent or children
class RelatedSubnetSerializer(serpy.Serializer):
    """
    address_id:
        description: The ID of the Address that owns the Subnet.
        type: integer
    address_range:
        description: The address range of the Subnet.
        type: string
    allocation:
        $ref: '#/components/schemas/Allocation'
    cloud:
        description: Flag stating whether or not this Subnet is designated for the Cloud.
        type: boolean
    created:
        description: Timestamp, in ISO format, of when the Subnet record was created.
        type: string
    gateway:
        description: The gateway address of the Subnet.
        type: string
    id:
        description: The ID of the Subnet record
        type: integer
    ips_in_use:
        description: The total number of IP Addresses that are in use in this Subnet
        type: integer
    modified_by:
        description: The ID of the User that last made changes to the Subnet record.
        type: integer
    name:
        description: The verbose name of the Subnet record.
        type: string
    subnets_in_use:
        description: The total number of Subnets that are in use in this Subnet
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Subnet record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the Subnet record that can be used to perform `Read`, `Update` and `Delete`.
        type: string
    virtual_router_id:
        description: The ID of the Virtual Router the subnet is configured on.
        type: integer
    vlan:
        description: The vlan in use for the Subnet.
        type: integer
    vxlan:
        description: The vxlan in use for the Subnet.
        type: integer
    """
    address_id = serpy.Field()
    address_range = serpy.Field()
    allocation = AllocationSerializer()
    cloud = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    gateway = serpy.Field()
    id = serpy.Field()
    ips_in_use = serpy.Field()
    modified_by = serpy.Field()
    subnets_in_use = serpy.Field()
    name = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    virtual_router_id = serpy.Field()
    vlan = serpy.Field()
    vxlan = serpy.Field()


class SubnetSerializer(RelatedSubnetSerializer):
    """
    address_id:
        description: The ID of the Address that owns the Subnet.
        type: integer
    address_range:
        description: The address range of the Subnet.
        type: string
    allocation:
        $ref: '#/components/schemas/Allocation'
    children:
        description: A list of Subnets to which this Subnet is the parent
        type: array
        items:
            $ref: '#/components/schemas/RelatedSubnet'
    cloud:
        description: Flag stating whether or not this Subnet is designated for the Cloud.
        type: boolean
    created:
        description: Timestamp, in ISO format, of when the Subnet record was created.
        type: string
    gateway:
        description: The gateway address of the Subnet.
        type: string
    id:
        description: The ID of the Subnet record
        type: integer
    ips_in_use:
        description: The total number of IP Addresses that are in use in this Subnet
        type: integer
    modified_by:
        description: The ID of the User that last made changes to the Subnet record.
        type: integer
    name:
        description: The verbose name of the Subnet record.
        type: string
    subnets_in_use:
        description: The total number of Subnets that are in use in this Subnet
        type: integer
    parent:
        $ref: '#/components/schemas/RelatedSubnet'
    virtual_router_id:
        description: The ID of the Virtual Router the subnet is configured on.
        type: integer
    vlan:
        description: The vlan in use for the Subnet.
        type: integer
    vxlan:
        description: The vxlan in use for the Subnet.
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Subnet record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the Subnet record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    children = RelatedSubnetSerializer(many=True, attr='children.iterator', call=True)
    parent = RelatedSubnetSerializer(required=False)


class SubnetSpaceSerializer(serpy.Serializer):
    """
    address_id:
        description: The ID of the Address that owns the Subnet.
        type: integer
    address_range:
        description: The address range of the Subnet.
        type: string
    cloud:
        description: Flag stating whether or not this Subnet is designated for the Cloud.
        type: boolean
    id:
        description: The ID of the Subnet record
        type: integer
    ips_in_use:
        description: The total number of IP Addresses that are in use in this Subnet
        type: integer
    modified_by:
        description: The ID of the User that last made changes to the Subnet record.
        type: integer
    name:
        description: The verbose name of the Subnet record.
        type: string
    subnets_in_use:
        description: The total number of Subnets that are in use in this Subnet
        type: integer
    virtual_router_id:
        description: The ID of the Virtual Router the subnet is configured on.
        type: integer
    vlan:
        description: The vlan in use for the Subnet.
        type: integer
    vxlan:
        description: The vxlan in use for the Subnet.
        type: integer
    """

    address_id = serpy.Field(required=False)
    address_range = serpy.Field()
    cloud = serpy.Field(required=False)
    id = serpy.Field(required=False)
    ips_in_use = serpy.Field(required=False)
    modified_by = serpy.Field(required=False)
    name = serpy.Field(required=False)
    subnets_in_use = serpy.Field(required=False)
    virtual_router_id = serpy.Field(required=False)
    vlan = serpy.Field(required=False)
    vxlan = serpy.Field(required=False)
