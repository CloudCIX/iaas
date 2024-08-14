"""
Error Codes for all of the methods in the Router service
"""

# List
iaas_router_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
iaas_router_list_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can list Router records.'

)

# Create
iaas_router_create_101 = 'The "asset_tag" parameter is invalid. "asset_tag" must be a valid integer.'
iaas_router_create_102 = 'The "capacity" parameter is invalid. "capacity" must be a valid integer.'
iaas_router_create_103 = 'The "credentials" parameter is invalid. "credentials" cannot be longer than 128 characters.'
iaas_router_create_104 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_router_create_105 = 'The "model" parameter is invalid. "model" is required.'
iaas_router_create_106 = 'The "model" parameter is invalid. "model" cannot be longer than 64 characters.'
iaas_router_create_107 = 'The "username" parameter is invalid. "username" cannot be longer than 250 characters.'
iaas_router_create_108 = (
    'The "management_interface" parameter is invalid. "management_interface" cannot be longer than 20 characters.'
)
iaas_router_create_109 = (
    'The "management_interface" parameter is invalid. "management_interface" is not a string containing only lower case'
    ' letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_create_110 = (
    'The "oob_interface" parameter is invalid. "oob_interface" cannot be longer than 20 characters.'
)
iaas_router_create_111 = (
    'The "oob_interface" parameter is invalid. "oob_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_create_112 = (
    'The "public_interface" parameter is invalid. "public_interface" cannot be longer than 20 characters.'
)
iaas_router_create_113 = (
    'The "public_interface" parameter is invalid. "public_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_create_114 = (
    'The "private_interface" parameter is invalid. "private_interface" cannot be longer than 20 characters.'
)
iaas_router_create_115 = (
    'The "private_interface" parameter is invalid. "private_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_create_116 = (
    'The "router_oob_interface" parameter is invalid. "router_oob_interface" cannot be longer than 20 characters.'
)
iaas_router_create_117 = (
    'The "router_oob_interface" parameter is invalid. "router_oob_interface" is not a string containing only lower case'
    ' letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_create_118 = 'The "subnets" parameter is invalid. "subnets" must be a list of Subnet IDs'
iaas_router_create_119 = 'The "subnets" parameter is invalid. "subnets" must have at least one Subnet ID in the list.'
iaas_router_create_120 = 'The "subnets" parameter is invalid. All Subnet IDs in the list must be an integer.'
iaas_router_create_121 = (
    'The "subnets" parameter is invalid. All Subnet IDs in the list must belong to a valid Subnet record belonging to '
    'your Region.'
)
iaas_router_create_122 = 'The "subnets" parameter is invalid. There can only be one /48 IPv6 Subnet on a Router.'
iaas_router_create_123 = 'The "subnets" parameter is invalid. The IPv6 Subnet mask for the Subnet ID must be a /48.'
iaas_router_create_124 = (
    'The "public_port_ips" parameter is invalid. "public_port_ips" must be a list of public IP addresses in the format '
    'of ["8.0.0.2", "91.103.1.2"]'
)
iaas_router_create_125 = (
    'The "public_port_ips" parameter is invalid. "public_port_ips" is required and cannot be an empty list.'
)
iaas_router_create_126 = 'The "public_port_ips" parameter is invalid. All IPs in the list  must be a valid IP Address.'
iaas_router_create_127 = 'The "public_port_ips" parameter is invalid. All IPs in the list must be a public IP Address.'
iaas_router_create_128 = (
    'The "public_port_ips" parameter is invalid. A VM IP address cannot be the network, gateway or broadcast address of'
    ' its Subnet.'
)
iaas_router_create_129 = (
    'The "public_port_ips" parameter is invalid. An IP Address with one of the specified ips already exists.'
)
iaas_router_create_130 = (
    'The "public_port_ips" parameter is invalid. One of the supplied IPs is not from a Subnet in your Address'
)

iaas_router_create_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can create Router records.'
)
# Read
iaas_router_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Router record.'
iaas_router_read_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can read Router records.'
)

# Update
iaas_router_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Router record.'
iaas_router_update_101 = 'The "asset_tag" parameter is invalid. "asset_tag" must be a valid integer.'
iaas_router_update_102 = 'The "capacity" parameter is invalid. "capacity" must be a valid integer.'
iaas_router_update_103 = 'The "credentials" parameter is invalid. "credentials" cannot be longer than 128 characters.'
iaas_router_update_104 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_router_update_105 = 'The "model" parameter is invalid. "model" is required.'
iaas_router_update_106 = 'The "model" parameter is invalid. "model" cannot be longer than 64 characters.'
iaas_router_update_107 = 'The "username" parameter is invalid. "username" cannot be longer than 250 characters.'
iaas_router_update_108 = (
    'The "management_interface" parameter is invalid. "management_interface" cannot be longer than 20 characters.'
)
iaas_router_update_109 = (
    'The "management_interface" parameter is invalid. "management_interface" is not a string containing only lower case'
    ' letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_update_110 = (
    'The "oob_interface" parameter is invalid. "oob_interface" cannot be longer than 20 characters.'
)
iaas_router_update_111 = (
    'The "oob_interface" parameter is invalid. "oob_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_update_112 = (
    'The "public_interface" parameter is invalid. "public_interface" cannot be longer than 20 characters.'
)
iaas_router_update_113 = (
    'The "public_interface" parameter is invalid. "public_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_update_114 = (
    'The "private_interface" parameter is invalid. "private_interface" cannot be longer than 20 characters.'
)
iaas_router_update_115 = (
    'The "private_interface" parameter is invalid. "private_interface" is not a string containing only lower case '
    'letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_update_116 = (
    'The "router_oob_interface" parameter is invalid. "router_oob_interface" cannot be longer than 20 characters.'
)
iaas_router_update_117 = (
    'The "router_oob_interface" parameter is invalid. "router_oob_interface" is not a string containing only lower case'
    ' letters, digits, a forward slash (/) or a dash (-) character.'
)
iaas_router_update_118 = 'The "subnets" parameter is invalid. "subnets" must be a list of Subnet IDs'
iaas_router_update_119 = 'The "subnets" parameter is invalid. "subnets" must have at least one Subnet ID in the list.'
iaas_router_update_120 = (
    'The "subnets" parameter is invalid. One of the subnets to be removed has /64 Subnets in use. Projects for '
    'these child subnets should be closed before removing Subnet from Router'
)
iaas_router_update_121 = (
    'The "subnets" parameter is invalid. One of the subnets to be removed has IP Addresses in use. VMs or Virtual'
    'Routers using these IP Addresses should be closed before removing Subnet from Router'
)
iaas_router_update_122 = 'The "subnets" parameter is invalid. All Subnet IDs in the list must be an integer.'
iaas_router_update_123 = (
    'The "subnets" parameter is invalid. All Subnet IDs in the list must belong to a valid Subnet record belonging to '
    'your Region.'
)
iaas_router_update_124 = 'The "subnets" parameter is invalid. There can only be one /48 IPv6 Subnet on a Router.'
iaas_router_update_125 = 'The "subnets" parameter is invalid. The IPv6 Subnet mask for the Subnet ID must be a /48.'
iaas_router_update_126 = (
    'The "public_port_ips" parameter is invalid. "public_port_ips" must be a list of public IP addresses in the format '
    'of ["8.0.0.2", "91.103.1.2"]'
)
iaas_router_update_127 = 'The "public_port_ips" parameter is invalid. "public_port_ips" cannot be an empty list.'
iaas_router_update_128 = 'The "public_port_ips" parameter is invalid. All IPs in the list  must be a valid IP Address.'
iaas_router_update_129 = 'The "public_port_ips" parameter is invalid. All IPs in the list must be a public IP Address.'
iaas_router_update_130 = (
    'The "public_port_ips" parameter is invalid. A VM IP address cannot be the network, gateway or broadcast address of'
    ' its Subnet.'
)
iaas_router_update_131 = (
    'The "public_port_ips" parameter is invalid. An IP Address with one of the specified ips already exists.'
)
iaas_router_update_132 = (
    'The "public_port_ips" parameter is invalid. One of the supplied IPs is not from a Subnet in your Address'
)
iaas_router_update_201 = (
    'You do not have permission to make this request. You can only update Routers that belong to your address'
)
