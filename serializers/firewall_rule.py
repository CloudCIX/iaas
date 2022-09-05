# libs
import serpy

__all__ = [
    'FirewallRuleSerializer',
]


class FirewallRuleSerializer(serpy.Serializer):
    """
    allow:
        description: A flag stating whether traffic matching the rule should be allowed through the firewall.
        type: boolean
    created:
        description: The date that the FirewallRule entry was created
        type: string
    debug_logging:
        description: A flag stating whether debug logging for the rule is active.
        type: boolean
    description:
        description: A verbose text field used to describe what the rule is used for.
        type: string
    destination:
        description: A Subnet or IP Address representing the destination value for the rule.
        type: string
    id:
        description: The ID of the firewall rule.
        type: integer
    order:
        description: |
            The position of the firewall rule in its Virtual Router.
            This is important as the Virtual Router will only search until it finds the first rule that matches the
            conditions.
        type: integer
    pci_logging:
        description: A flag stating whether PCI logging for the rule is active.
        type: boolean
    port:
        description: |
            The port to use when checking incoming traffic against this FirewallRule.
            If this number is -1, then it will match all ports.
        type: integer
    protocol:
        description: |
            The protocol to use when checking incoming traffic against this FirewallRule.
            Will be either `tcp` or `udp`, but can also be `any` if the port value is set to -1 to allow any application
            through the firewall.
        type: string
    source:
        description: A Subnet or IP Address representing the source value for the rule.
        type: string
    updated:
        description: The date that the FirewallRule entry was last updated
        type: string
    virtual_router_id:
        description: The ID of the VirtualRouter that this FirewallRule is a part of.
        type: integer
    """
    allow = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    debug_logging = serpy.Field()
    description = serpy.Field()
    destination = serpy.Field()
    id = serpy.Field()
    order = serpy.Field()
    pci_logging = serpy.Field()
    port = serpy.Field()
    protocol = serpy.Field()
    source = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    virtual_router_id = serpy.Field()
