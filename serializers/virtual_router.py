# libs
import serpy
# local
from .firewall_rule import FirewallRuleSerializer
from .ip_address import IPAddressSerializer
from .project import ProjectSerializer


__all__ = [
    'BaseVirtualRouterSerializer',
    'VirtualRouterSerializer',
]


class BaseVirtualRouterSerializer(serpy.Serializer):
    """
    created:
        description: The date that the VirtualRouter entry was created
        type: string
    id:
        description: The ID of the VirtualRouter.
        type: integer
    router_id:
        description: The ID of the Router
        type: integer
    state:
        description: The state of the VirtualRouter.
        type: integer
    subnets:
        description: |
            An array of the Subnet address ranges on the Virtual Router.
        type: array
        items:
            type: object
            properties:
                address_id:
                    description: The ID of the Address that owns the Subnet.
                    type: integer
                address_range:
                    description: The address range of the Subnet.
                    type: string
                id:
                    description: The ID of the Subnet record
                    type: integer
                modified_by:
                    description: The ID of the User that last made changes to the Subnet record.
                    type: integer
                name:
                    description: The verbose name of the Subnet record.
                    type: string
                vlan:
                    description: The vlan in use for the Subnet.
                    type: integer
                vxlan:
                    description: The vxlan in use for the Subnet.
                    type: integer
    updated:
        description: The date that the VirtualRouter entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the VirtualRouter record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    router_id = serpy.Field()
    state = serpy.Field()
    subnets = serpy.Field(attr='get_subnets', call=True, required=False)
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)


class VirtualRouterSerializer(BaseVirtualRouterSerializer):
    """
    created:
        description: The date that the VirtualRouter entry was created
        type: string
    firewall_rules:
        description: An array of user defined Firewall Rules in the Virtual Router
        type: array
        items:
            $ref: '#/components/schemas/FirewallRule'
    id:
        description: The ID of the VirtualRouter.
        type: integer
    ip_address:
        $ref: '#/components/schemas/IPAddress'
    project:
        $ref: '#/components/schemas/Project'
    router_id:
        description: The ID of the Router
        type: integer
    state:
        description: The state of the VirtualRouter.
        type: integer
    subnets:
        description: |
            An array of the Subnet address ranges on the Virtual Router.
        type: array
        items:
            type: object
            properties:
                address_id:
                    description: The ID of the Address that owns the Subnet.
                    type: integer
                address_range:
                    description: The address range of the Subnet.
                    type: string
                id:
                    description: The ID of the Subnet record
                    type: integer
                modified_by:
                    description: The ID of the User that last made changes to the Subnet record.
                    type: integer
                name:
                    description: The verbose name of the Subnet record.
                    type: string
                vlan:
                    description: The vlan in use for the Subnet.
                    type: integer
                vxlan:
                    description: The vxlan in use for the Subnet.
                    type: integer
    updated:
        description: The date that the VirtualRouter entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the VirtualRouter record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    firewall_rules = FirewallRuleSerializer(attr='firewall_rules.iterator', call=True, many=True)
    ip_address = IPAddressSerializer()
    project = ProjectSerializer()
