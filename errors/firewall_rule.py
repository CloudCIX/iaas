"""
Errors for FirewallRule services
"""

# Create
iaas_firewall_rule_create_101 = (
    'The "allow" parameter is invalid. "allow" is required and must be a valid boolean value.'
)
iaas_firewall_rule_create_102 = 'The "source" parameter is invalid. "source" is required.'
iaas_firewall_rule_create_103 = (
    'The "source" parameter is invalid. "source" must be a string containing a valid CIDR address or address range.'
)
iaas_firewall_rule_create_104 = 'The "destination" parameter is invalid. "destination" is required.'
iaas_firewall_rule_create_105 = (
    'The "destination" parameter is invalid. "destination" must be a string containing a valid CIDR address or '
    'address range.'
)
iaas_firewall_rule_create_106 = (
    'The "source" and "destination" parameters are invalid together. "source" and "destination" must use the same '
    'IP version (4 or 6)'
)
iaas_firewall_rule_create_107 = (
    'The "source" and "destination" parameters are invalid together. One of these values must correspond to a public '
    'address range, and the other to a private one.'
)
iaas_firewall_rule_create_108 = (
    'An error occurred when attempting to connect to the iaas API to read the Subnets in the Virtual Router. Please '
    'try again later or contact CloudCIX Support if this persists.'
)
iaas_firewall_rule_create_109 = (
    'One of the "source" or "destination" parameters are invalid. Please ensure that the private subnet chosen is '
    'one of the Subnets in the Project.'
)
iaas_firewall_rule_create_110 = (
    'The "protocol" parameter is invalid. "protocol" is required and must be one of the following: "tcp", "udp", "any".'
)
iaas_firewall_rule_create_111 = 'The "port" parameter is invalid. "port" is required if the protocol is `tcp` or `udp`.'
iaas_firewall_rule_create_112 = (
    'The "port" parameter is invalid. For a range of ports to be valid it must be in the string format of '
    '"number-number" e.g. "20-25".'
)
iaas_firewall_rule_create_113 = (
    'The "port" parameter is invalid. Both instances on either side of the "-" must be a string format of a number '
    'between 1 and 65535 inclusive.'
)
iaas_firewall_rule_create_114 = (
    'The "port" parameter is invalid. "port" must be a string format of a number between 1 and 65535 inclusive.'
)
iaas_firewall_rule_create_115 = (
    'The "port" parameter is invalid. "port" must be a string format of a number or numbers separated by a "-" '
    'e.g. "22" or "20-25".'
)
iaas_firewall_rule_create_116 = (
    'he "debug_logging" parameter is invalid. "debug_logging" is optional and must be a valid boolean value.'
)
iaas_firewall_rule_create_117 = (
    'The "pci_logging" parameter is invalid. "pci_logging" is optional and must be a valid boolean value.'
)
iaas_firewall_rule_create_118 = (
    'The "pci_logging" parameter is invalid. "pci_logging" can only be True if the "allow" parameter is True.'
)
