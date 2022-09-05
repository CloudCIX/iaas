"""
Error Codes for all of the Methods in the Route Service
"""
# Create
iaas_route_create_101 = 'The "local_subnet" parameter is invalid. "local_subnet" is required.'
iaas_route_create_102 = 'The "local_subnet" parameter is invalid. `local_subnet` must  be a valid address range.'
iaas_route_create_103 = (
    'The "local_subnet" parameter is invalid. "local_subnet" does not correspond to any valid Subnet.'
)

iaas_route_create_104 = 'The "remote_subnet" parameter is invalid. "remote_subnet" is required.'
iaas_route_create_105 = (
    'The "remote_subnet" parameter is invalid. "remote_subnet" must be a string containing a valid address range.'
)
iaas_route_create_106 = (
    'The "remote_subnet" parameter is invalid. The sent "remote_subnet" overlaps with a Subnet configured in this VPN'
    ' Project'
)
iaas_route_create_107 = (
    'The "remote_subnet" parameter is invalid. The sent "remote_subnet" overlaps with a remote subnet on another VPN in'
    ' the same Project'
)
iaas_route_create_108 = (
    'The "remote_subnet" parameter is invalid. The remote subnet for a Dynamic Secure Connect VPN must be a /24 from '
    'the RFC1918 172.16.0.0/12.'
)
iaas_route_create_109 = (
    'There are currently No available Dynamic Remote Subnets associated with this region. Please contact CloudCIX '
    'Support.'
)
iaas_route_create_110 = (
    'The "remote_subnet" parameter is invalid. The remote subnet is not available. Please choose another from the '
    'dynamic_remote_subnet list.'
)
# Update
iaas_route_update_101 = 'The "local_subnet" parameter is invalid. "local_subnet" is required.'
iaas_route_update_102 = 'The "local_subnet" parameter is invalid. `local_subnet` must  be a valid address range.'
iaas_route_update_103 = (
    'The "local_subnet" parameter is invalid. "local_subnet" does not correspond to any valid Subnet.'
)

iaas_route_update_104 = 'The "remote_subnet" parameter is invalid. "remote_subnet" is required.'
iaas_route_update_105 = (
    'The "remote_subnet" parameter is invalid. "remote_subnet" must be a string containing a valid address range.'
)
iaas_route_update_106 = (
    'The "remote_subnet" parameter is invalid. The sent "remote_subnet" overlaps with a Subnet configured in this VPN'
    ' Project'
)
iaas_route_update_107 = (
    'The "remote_subnet" parameter is invalid. The sent "remote_subnet" overlaps with a remote subnet on another VPN in'
    ' the same Project'
)
iaas_route_update_108 = (
    'The "remote_subnet" parameter is invalid. The remote subnet for a Dynamic Secure Connect VPN must be a /24 from '
    'the RFC1918 172.16.0.0/12.'
)
iaas_route_update_109 = (
    'There are currently No available Dynamic Remote Subnets associated with this region. Please contact CloudCIX '
    'Support.'
)
iaas_route_update_110 = (
    'The "remote_subnet" parameter is invalid. The remote subnet is not available. Please choose another from the '
    'dynamic_remote_subnet list.'
)
