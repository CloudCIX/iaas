"""
Error Codes for all of the methods in the VPN service
"""

# List
iaas_vpn_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_vpn_create_001 = (
    'This request cannot be completed. The chosen Virtual Router cannot be updated to the UPDATE state.'
)
iaas_vpn_create_002 = (
    'There was an error creating your VPN. CloudCIX has hit an internal capacity limit. Our team have been notified.'
)
iaas_vpn_create_101 = 'The "virtual_router_id" parameter is invalid. "virtual_router_id" is required.'
iaas_vpn_create_102 = 'The "virtual_router_id" parameter is invalid. "virtual_router_id" must be a valid integer.'
iaas_vpn_create_103 = (
    'The "virtual_router_id" parameter is invalid. "virtual_router_id" must correspond with a valid VirtualRouter '
    'record.'
)
iaas_vpn_create_104 = (
    'The "virtual_router_id" parameter is invalid. "virtual_router_id" must correspond with a Virtual Router in a '
    'Project owned by your Address.'
)


iaas_vpn_create_105 = 'The "ike_authentication" parameter is invalid. "ike_authentication" is required.'
iaas_vpn_create_106 = (
    'The "ike_authentication" parameter is invalid. "ike_authentication" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_107 = 'The "ike_dh_groups" parameter is invalid. "ike_dh_groups" is required.'
iaas_vpn_create_108 = (
    'The "ike_dh_groups" parameter is invalid. "ike_dh_groups" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_109 = 'The "ike_encryption" parameter is invalid. "ike_encryption" is required.'
iaas_vpn_create_110 = (
    'The "ike_encryption" parameter is invalid. "ike_encryption" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_111 = 'The "ike_lifetime" parameter is invalid. "ike_lifetime" must be a valid integer.'
iaas_vpn_create_112 = (
    'The "ike_lifetime" parameter is invalid. "ike_lifetime" must be in the range of 180 - 86400 inclusive.'
)
iaas_vpn_create_113 = 'The "ike_mode" parameter is invalid. The supplied "ike_mode" is not one of the allowed choices.'
iaas_vpn_create_114 = 'The "ike_pre_shared_key" parameter is invalid. "ike_pre_shared_key" is required.'
iaas_vpn_create_115 = (
    'The "ike_pre_shared_key" parameter is invalid. "ike_pre_shared_key" cannot contain any of '
    '\", \', @, +, -, =, /, \\,| and space these special characters.'
)
iaas_vpn_create_116 = (
    'The "ike_pre_shared_key" parameter is invalid. When the IKE encryption algorithm is `des-cbc`, the max allowed '
    'length for the pre shared key is 8 characters.'
)
iaas_vpn_create_117 = (
    'The "ike_pre_shared_key" parameter is invalid. When the IKE encryption algorithm is `3des-cbc`, the max allowed '
    'length for the pre shared key is 24 characters.'
)
iaas_vpn_create_118 = (
    'The "ike_pre_shared_key" parameter is invalid. The pre shared key cannot be longer than 255 characters.'
)
iaas_vpn_create_120 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" must be a valid IP Address.'
iaas_vpn_create_121 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" must be IPv4 at the moment.'

iaas_vpn_create_122 = (
    'The "ike_version" parameter is invalid. The supplied "ike_version" is not one of the allowed choices.'
)
iaas_vpn_create_123 = 'The "ipsec_authentication" parameter is invalid. "ipsec_authentication" is required.'
iaas_vpn_create_124 = (
    'The "ipsec_authentication" parameter is invalid. "ipsec_authentication" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_125 = 'The "ipsec_encryption" parameter is invalid. "ipsec_encryption" is required.'
iaas_vpn_create_126 = (
    'The "ipsec_encryption" parameter is invalid. "ipsec_encryption" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_127 = (
    'The "ipsec_establish_time" parameter is invalid. The supplied "ipsec_establish_time" is not one of the allowed '
    'choices.'
)
iaas_vpn_create_128 = (
    'The "ipsec_pfs_groups" parameter is invalid. "ipsec_pfs_groups" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_create_129 = 'The "ipsec_lifetime" parameter is invalid. "ipsec_lifetime" must be a valid integer.'
iaas_vpn_create_130 = (
    'The "ipsec_lifetime" parameter is invalid. "ipsec_lifetime" must be in the range of 180 - 86400 inclusive.'
)
iaas_vpn_create_131 = 'The "routes" parameter is invalid. "routes" is required and must be a list.'
iaas_vpn_create_132 = 'The "routes" parameter is invalid. "routes" cannot be empty.'
iaas_vpn_create_133 = 'The "traffic_selector" parameter is invalid. "traffic_selector" must be a boolean.'
iaas_vpn_create_134 = 'The "vpn_type" parameter is invalid. The supplied "vpn_type" is not one of the allowed choices.'
iaas_vpn_create_135 = 'The "dns" parameter is invalid. "dns" is required for Dynamic Secure Connect VPN tunnels.'
iaas_vpn_create_136 = 'The "dns" parameter is invalid. "dns" must be a valid IP Address.'
iaas_vpn_create_137 = 'The "dns" parameter is invalid. "dns" must be IPv4 at the moment.'
iaas_vpn_create_138 = 'The "vpn_clients" parameter is invalid. "vpn_clients" is required and must be a list.'
iaas_vpn_create_139 = 'The "vpn_clients" parameter is invalid. "vpn_clients" cannot be empty.'
iaas_vpn_create_140 = (
    'The "ike_gateway_type" parameter is invalid. "ike_gateway_type" must be either \'public_ip\' or \'hostname\'.'
)
iaas_vpn_create_141 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" is required.'
iaas_vpn_create_142 = 'The "ike_gateway_value" paramter is invalid. "ike_gateway_value" must be a valid FQDN.'

# Read
iaas_vpn_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid VPN record.'
iaas_vpn_read_201 = 'You do not have permission to make this request. Robots can only read the VPNs in their region.'
iaas_vpn_read_202 = (
    'You do not have permission to make this request. A global active user can only read VPNs that are owned by '
    'Addresses in their Member.'
)
iaas_vpn_read_203 = 'You do not have permission to make this request. Can only read VPNs that you own.'

# Update
iaas_vpn_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid VPN record.'
iaas_vpn_update_002 = (
    'This request cannot be completed. The chosen Virtual Router cannot be updated to the UPDATE state.'
)
iaas_vpn_update_101 = 'The "ike_authentication" parameter is invalid. "ike_authentication" is required.'
iaas_vpn_update_102 = (
    'The "ike_authentication" parameter is invalid. "ike_authentication" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_103 = 'The "ike_dh_groups" parameter is invalid. "ike_dh_groups" is required.'
iaas_vpn_update_104 = (
    'The "ike_dh_groups" parameter is invalid. "ike_dh_groups" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_105 = 'The "ike_encryption" parameter is invalid. "ike_encryption" is required.'
iaas_vpn_update_106 = (
    'The "ike_encryption" parameter is invalid. "ike_encryption" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_107 = 'The "ike_lifetime" parameter is invalid. "ike_lifetime" must be a valid integer.'
iaas_vpn_update_108 = (
    'The "ike_lifetime" parameter is invalid. "ike_lifetime" must be in the range of 180 - 86400 inclusive.'
)
iaas_vpn_update_109 = 'The "ike_mode" parameter is invalid. The supplied "ike_mode" is not one of the allowed choices.'
iaas_vpn_update_110 = 'The "ike_pre_shared_key" parameter is invalid. "ike_pre_shared_key" is required.'
iaas_vpn_update_111 = (
    'The "ike_pre_shared_key" parameter is invalid. "ike_pre_shared_key" cannot contain any of '
    '\", \', @, +, -, =, /, \\,|  these special characters.'
)
iaas_vpn_update_112 = (
    'The "ike_pre_shared_key" parameter is invalid. When the IKE encryption algorithm is `des-cbc`, the max allowed '
    'length for the pre shared key is 8 characters.'
)
iaas_vpn_update_113 = (
    'The "ike_pre_shared_key" parameter is invalid. When the IKE encryption algorithm is `3des-cbc`, the max allowed '
    'length for the pre shared key is 24 characters.'
)
iaas_vpn_update_114 = (
    'The "ike_pre_shared_key" parameter is invalid. The pre shared key cannot be longer than 255 characters.'
)
iaas_vpn_update_116 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" must be a valid IP Address.'
iaas_vpn_update_117 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" must be IPv4 at the moment.'
iaas_vpn_update_118 = (
    'The "ike_version" parameter is invalid. The supplied "ike_version" is not one of the allowed choices.'
)
iaas_vpn_update_119 = 'The "ipsec_authentication" parameter is invalid. "ipsec_authentication" is required.'
iaas_vpn_update_120 = (
    'The "ipsec_authentication" parameter is invalid. "ipsec_authentication" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_121 = 'The "ipsec_encryption" parameter is invalid. "ipsec_encryption" is required.'
iaas_vpn_update_122 = (
    'The "ipsec_encryption" parameter is invalid. "ipsec_encryption" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_123 = (
    'The "ipsec_establish_time" parameter is invalid. The supplied "ipsec_establish_time" is not one of the allowed '
    'choices.'
)
iaas_vpn_update_124 = (
    'The "ipsec_pfs_groups" parameter is invalid. "ipsec_pfs_groups" contains an entry that is not one of the '
    'valid choices.'
)
iaas_vpn_update_125 = 'The "ipsec_lifetime" parameter is invalid. "ipsec_lifetime" must be a valid integer.'
iaas_vpn_update_126 = (
    'The "ipsec_lifetime" parameter is invalid. "ipsec_lifetime" must be in the range of 180 - 86400 inclusive.'
)
iaas_vpn_update_127 = 'The "routes" parameter is invalid. "routes" is required and must be a list.'
iaas_vpn_update_128 = 'The "routes" parameter is invalid. "routes" cannot be empty.'
iaas_vpn_update_129 = (
    'The "routes" parameter is invalid. One of the items in "routes" has an "id" value that does not correspond to a '
    'valid Route record.'
)
iaas_vpn_update_130 = 'The "traffic_selector" parameter is invalid. "traffic_selector" must be a boolean.'
iaas_vpn_update_131 = 'The "dns" parameter is invalid. "dns" must be a valid IP Address.'
iaas_vpn_update_132 = 'The "dns" parameter is invalid. "dns" must be IPv4 at the moment.'
iaas_vpn_update_133 = 'The "vpn_clients" parameter is invalid. "vpn_clients" is required and must be a list.'
iaas_vpn_update_134 = 'The "vpn_clients" parameter is invalid. "vpn_clients" cannot be empty.'
iaas_vpn_update_135 = (
    'The "vpn_clients" parameter is invalid. One of the items in "vpn_clients" has an "id" value that does not '
    'correspond to a valid VPNClient record.'
)
iaas_vpn_update_136 = (
    'The "ike_gateway_type" parameter is invalid. "ike_gateway_type" must be either \'public_ip\' or \'hostname\'.'
)
iaas_vpn_update_137 = 'The "ike_gateway_value" parameter is invalid. "ike_gateway_value" is required.'
iaas_vpn_update_138 = 'The "ike_gateway_value" paramter is invalid. "ike_gateway_value" must be a valid FQDN.'
iaas_vpn_update_201 = (
    'You do not have permission to make this request. Robots can only update the VPNs in their region.'
)
iaas_vpn_update_202 = 'You do not have permission to make this request. Can only update VPNs that you own.'

# Delete
iaas_vpn_delete_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid VPN record.'
iaas_vpn_delete_002 = (
    'This request cannot be completed. The chosen Virtual Router cannot be updated to the UPDATE state.'
)
iaas_vpn_delete_201 = (
    'You do not have permission to make this request. Robots can only delete the VPNs in their region.'
)
iaas_vpn_delete_202 = 'You do not have permission to make this request. Can only delete VPNs that you own.'
