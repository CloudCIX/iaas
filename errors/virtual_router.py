"""
Error Codes for all of the methods in the VirtualRouter service
"""

# List
iaas_virtual_router_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_virtual_router_create_101 = 'The "project_id" parameter is invalid. "project_id" is required.'
iaas_virtual_router_create_102 = 'The "project_id" parameter is invalid. "project_id" must be a valid integer.'
iaas_virtual_router_create_103 = (
    'The "project_id" parameter is invalid. "project_id" does not correspond with a valid Project record.'
)
iaas_virtual_router_create_104 = (
    'The "project_id" parameter is invalid. The chosen Project already has a VirtualRouter record associated with it.'
)
iaas_virtual_router_create_105 = (
    'There are currently no valid Phantom Routers to place the Phantom VirtualRouter onto in this region. Please '
    'contact CloudCIX Support.'
)
iaas_virtual_router_create_106 = (
    'There are currently no valid Routers to place the VirtualRouter onto in this region. Please contact CloudCIX '
    'Support.'
)
iaas_virtual_router_create_107 = (
    'There are currently no space available to place the VirtualRouter onto in this regions Router. Please contact '
    'CloudCIX Support.'
)
iaas_virtual_router_create_108 = (
    'There are currently no valid IP Addresses  associated with the Router to place the VirtualRouter onto in this '
    'region. Please contact CloudCIX Support.'
)
iaas_virtual_router_create_109 = (
    'There are currently no available IP Addresses associated with the Router to place the VirtualRouter onto in this '
    'region. Please contact CloudCIX Support.'
)

# Read
iaas_virtual_router_read_001 = (
    'The "pk" path parameter is invalid. "pk" does not correspond to a valid VirtualRouter record.'
)
iaas_virtual_router_read_201 = (
    'You do not have permission to make this request. Robots may only read VirtualRouters that are in their own region.'
)
iaas_virtual_router_read_202 = (
    'You do not have permission to make this request. A global active user can only read VirtualRouters that are '
    'related to Projects for Addresses in their Member.'
)
iaas_virtual_router_read_203 = (
    'You do not have permission to make this request. Users can only read VirtualRouters that are related to Projects '
    'that belong to their Address.'
)

# Update
iaas_virtual_router_update_001 = (
    'The "pk" path parameter is invalid. "pk" does not correspond to a valid VirtualRouter record.'
)
iaas_virtual_router_update_002 = (
    'There was an error creating your cloud Subnet. CloudCIX has hit an internal capacity limit. Our team have been '
    'notified.'
)
iaas_virtual_router_update_003 = (
    'You cannot currently scrub this Virtual Router. There are active VMs still in the Project. Scrub and Close all '
    'VMs before scrubbing this Virtual Router.'
)
iaas_virtual_router_update_101 = 'The "state" parameter is invalid. "state" must be a valid integer.'
iaas_virtual_router_update_102 = (
    'The "state" parameter is invalid. "state" must be within the range of 1 to 17 inclusive.'
)
iaas_virtual_router_update_103 = (
    'The "state" parameter is invalid. The Virtual Router cannot be updated out of its current state. Please wait for '
    'Robot to finish whatever task it is running and try again.'
)
iaas_virtual_router_update_104 = (
    'The "state" parameter is invalid. The requested state change is invalid. Please check the API docs to see the '
    'full details of what state changes are allowed.'
)
iaas_virtual_router_update_105 = (
    'The "subnets" parameter is invalid. "subnets" must be a list of dictionaries in the format of '
    '[{"address_range": "1.1.1.0/24", "name": "Web Server, id: 1"}]'
)
iaas_virtual_router_update_106 = (
    'The "subnets" parameter is invalid. "subnets" is required and cannot be an empty list.'
)
iaas_virtual_router_update_107 = (
    'There was an error creating your cloud Subnet. The associated Project does not have a corresponding ASN in the DB.'
)
iaas_virtual_router_update_108 = (
    'One of the subnets "address_range" parameter is invalid. "address_range" must be a string containing a valid '
    ' Subnet.'
)
iaas_virtual_router_update_109 = (
    'One of the subnets "address_range" parameter is invalid. The gateway for a cloud "address_range" cannot be the '
    'network or broadcast address of the Subnet.'
)
iaas_virtual_router_update_110 = (
    'One of the subnets "address_range" parameter is invalid. One of the sent "address_range" overlaps with another of '
    'the sent "address_range"'
)
iaas_virtual_router_update_111 = (
    'The "subnets" parameter is invalid. One of the sent "subnet" overlaps with a remote subnet on a VPN in this '
    'Project.'
)
iaas_virtual_router_update_112 = (
    'One of the subnets "address_range" parameter is invalid. "address_range" from a RFC 1918 Private-Use Network, '
    '10.0.0.0/8, 172.16.0.0/12 or 192.168.0.0/16'
)
iaas_virtual_router_update_113 = (
    'One of the subnets "id" parameter is invalid. "id" does not correspond to a valid Subnet record.'
)
iaas_virtual_router_update_201 = (
    'You do not have permission to make this request. Robots may only update VirtualRouters that are in their own '
    'region.'
)
iaas_virtual_router_update_202 = (
    'You do not have permission to make this request. Users can only update VirtualRouters that are related to '
    'Projects that belong to their Address.'
)
iaas_virtual_router_update_203 = (
    'You do not have permission to make this request. A User must be public to update Virtual Routers.'
)
