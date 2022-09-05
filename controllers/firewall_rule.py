# stdlib
from typing import Optional
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
from jaeger_client import Span
from rest_framework.request import QueryDict, Request
# local
from iaas.models import FirewallRule, Subnet, VirtualRouter

__all__ = [
    'FirewallRuleCreateController',
]

PROTOCOL_CHOICES = dict(FirewallRule.PROTOCOL_CHOICES)
PORT_RANGE = range(1, 65536)
PORT_REQUIRED_PROTOCOLS = (
    FirewallRule.PROTOCOL_TCP,
    FirewallRule.PROTOCOL_UDP,
)


class FirewallRuleCreateController(ControllerBase):
    """
    Validates data used to create a new Firewall Rule.
    Order is managed externally, since the only way to create firewall rules is through the cloud views.
    """
    # Retain some information between validation methods
    source_is_private = False
    source_version = 4
    private_subnet: Optional[netaddr.IPNetwork] = None

    class Meta(ControllerBase.Meta):
        """
        Assign the model and validation order for fields.
        """
        model = FirewallRule
        validation_order = (
            'allow',
            'source',
            'destination',
            'private_subnet',
            'protocol',
            'port',
            'description',
            'debug_logging',
            'pci_logging',
        )

    def __init__(
            self,
            request: Request,
            data: QueryDict,
            span: Optional[Span],
            virtual_router: VirtualRouter,
            order: int,
    ) -> None:
        """
        Override the init to allow for adding extra fields from outside into the system.
        :param request: The request sent by the User
        :param data: The data being validated. Either request.GET or request.POST depending on the method
        :param span: A Span instance that is the parent span of the controller. Passing this in will allow us to record
                     time taken to run the validation methods in the controller.
        :param virtual_router: The virtual router being used to house the created FirewallRule
        :param order: The order of the firewall rule in the virtual router
        """
        super(FirewallRuleCreateController, self).__init__(request=request, data=data, span=span)
        self.cleaned_data['virtual_router'] = virtual_router
        self.cleaned_data['order'] = order

    def validate_allow(self, allow: Optional[bool]) -> Optional[str]:
        """
        description: |
            A flag that states whether traffic matching this rule should be allowed to pass through the firewall
        type: boolean
        """
        if allow not in {True, False}:
            return 'iaas_firewall_rule_create_101'
        self.cleaned_data['allow'] = allow
        return None

    def validate_source(self, source: Optional[str]) -> Optional[str]:
        """
        description: |
            A Subnet or IP Address that indicates what the source of traffic should be in order to match this rule.
            Can also be just a `*` character, which will indicate that any source is allowed.

            Please note that out of source and destination, one must be a public range and the other must be a private
            range.
            Also, both source and destination must use the same IP Version.
        type: string
        """
        if source is None:
            return 'iaas_firewall_rule_create_102'

        # Special case handling for '*'
        if source == '*':
            source = '0.0.0.0/0'

        # Ensure it's a valid Subnet format
        try:
            network = netaddr.IPNetwork(source)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_firewall_rule_create_103'

        # Save some information about the source network
        self.source_version = network.version
        self.source_is_private = network.is_private()
        if self.source_is_private:
            self.private_subnet = network

        # Save the cidr for the subnet
        self.cleaned_data['source'] = str(network.cidr)
        return None

    def validate_destination(self, destination: Optional[str]) -> Optional[str]:
        """
        description: |
            A Subnet or IP Address that indicates what the destination of traffic should be in order to match this rule.
            Can also be just a `*` character, which will indicate that any destination is allowed.

            Please note that out of source and destination, one must be a public range and the other must be a private
            range.
            Also, both source and destination must use the same IP Version.
        type: string
        """
        if destination is None:
            return 'iaas_firewall_rule_create_104'

        # Special case handling for '*'
        if destination == '*':
            destination = '0.0.0.0/0'

        # Ensure it's a valid Subnet format
        try:
            network = netaddr.IPNetwork(destination)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_firewall_rule_create_105'

        # Check that the given source and destination are compatible
        # IP Versions
        if self.source_version != network.version:
            return 'iaas_firewall_rule_create_106'
        # One is private one is public
        if self.source_is_private == network.is_private():
            return 'iaas_firewall_rule_create_107'

        if network.is_private():
            self.private_subnet = network

        # Save the cidr for the subnet
        self.cleaned_data['destination'] = str(network.cidr)
        return None

    def validate_private_subnet(self, private_subnet) -> Optional[str]:
        """
        description: Ensure the valid Subnet exists in the Project's VirtualRouter
        generative: true
        """
        # If we have no private subnet then there was a mistake so just return
        if self.private_subnet is None:
            return None

        subnets = Subnet.objects.filter(
            virtual_router_id=self.cleaned_data['virtual_router'].pk,
        ).values('address_range')

        for subnet in subnets:
            network = netaddr.IPNetwork(subnet['address_range'])
            if self.private_subnet in network:
                return None

        # If we get here, we didn't find any matches
        return 'iaas_firewall_rule_create_109'

    def validate_protocol(self, protocol: Optional[str]) -> Optional[str]:
        """
        description: |
            A string that indicates what protocol traffic should be using in order to match this rule.
            The currently supported protocols are as following;
                - 'icmp'
                - 'tcp'
                - 'udp'

            The special case protocol 'any' is allowed and allows any protocol through in these situations.
            This is to allow the user to set up rules in the firewall that allow all traffic through, if they don't
            care about having a firewall for their project.
        type: string
        """
        if protocol is None:
            protocol = ''
        protocol = str(protocol).strip().lower()

        if protocol not in PROTOCOL_CHOICES:
            return 'iaas_firewall_rule_create_110'

        self.cleaned_data['protocol'] = protocol
        return None

    def validate_port(self, port: Optional[str]) -> Optional[str]:
        """
        description: |
            A string that indicates what the destination port of traffic should be in order to match this rule.
            The range for valid ports are between 1 - 65535 inclusive.
            Allowed Values:
                `22`: Only port 22 is allowed
                `20-25`: Ports between 20 and 25 inclusive are allowed
                ``: No port is required if the protocol is 'any' or 'icmp'
        type: string
        """
        if 'protocol' not in self.cleaned_data:
            return None
        protocol = self.cleaned_data['protocol']

        if port is None:
            if protocol in PORT_REQUIRED_PROTOCOLS:
                return 'iaas_firewall_rule_create_111'
            return None

        try:
            if '-' in port:
                items = port.split('-')
                if len(items) >= 3:
                    return 'iaas_firewall_rule_create_112'
                for item in items:
                    if int(item) not in PORT_RANGE:
                        return 'iaas_firewall_rule_create_113'
            else:
                if int(port) not in PORT_RANGE:
                    return 'iaas_firewall_rule_create_114'
        except (TypeError, ValueError):
            return 'iaas_firewall_rule_create_115'

        self.cleaned_data['port'] = port
        return None

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: An optional description of what the rule is for.
        type: string
        required: false
        """
        if description is None:
            description = ''
        description = str(description).strip()
        self.cleaned_data['description'] = description
        return None

    def validate_debug_logging(self, debug_logging: Optional[bool]) -> Optional[str]:
        """
        description: |
            A flag that states the current debug logging status
        type: boolean
        """
        if debug_logging is None:
            self.cleaned_data['debug_logging'] = False
            return None
        if debug_logging not in {True, False}:
            return 'iaas_firewall_rule_create_116'
        self.cleaned_data['debug_logging'] = debug_logging

        return None

    def validate_pci_logging(self, pci_logging: Optional[bool]) -> Optional[str]:
        """
        description: |
            A flag that states the current PCI logging status. Only allow rules can have PCI logging active
        type: boolean
        """
        if pci_logging is None:
            self.cleaned_data['pci_logging'] = False
            return None
        if pci_logging not in {True, False}:
            return 'iaas_firewall_rule_create_117'
        if 'allow' not in self.cleaned_data:
            return None

        if pci_logging and not self.cleaned_data['allow']:
            return 'iaas_firewall_rule_create_118'
        self.cleaned_data['pci_logging'] = pci_logging
        return None
