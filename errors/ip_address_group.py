"""
Error Codes for all Methods in the IP Address Group Service
"""

# list
iaas_ip_address_group_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
# read
iaas_ip_address_group_read_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid IP Address Group record.'
)
# create
iaas_ip_address_group_create_101 = 'The "member_id" parameter is invalid. "member_id" must be a valid integer.'
iaas_ip_address_group_create_102 = (
    'The "name" parameter is invalid. "name" is required. "name" can only contain uppercase letters, lowercase letters,'
    'digits, a hypen (-) or an underscore (_) and the "name" must start with a letter.'
)
iaas_ip_address_group_create_103 = (
    'The "name" parameter is invalid. "name" is already in use for another IP Address Group within the Member.'
)
iaas_ip_address_group_create_104 = 'The "version" parameter is invalid. "version" must be an integer, 4 or 6.'
iaas_ip_address_group_create_105 = 'The "version" parameter is invalid. "version" must be 4 or 6.'
iaas_ip_address_group_create_106 = 'The "cidrs" parameter is invalid. "cidrs" is required and must be a list.'
iaas_ip_address_group_create_107 = (
    'The "cidrs" parameter is invalid. There must be at least one CIDR item in the "cidrs" list'
)
iaas_ip_address_group_create_108 = (
    'One of the items in the "cidrs" parameter is invalid. Each item must be a valid address.'
)
iaas_ip_address_group_create_109 = (
    'One of the items in the "cidrs" parameter is invalid. Each item must have the same network version as the sent '
    'version for this instance.'
)
iaas_ip_address_group_create_201 = (
    'You do not have permission to make this request. Your Member must be self managed in order to create an IP '
    'Address Group.'
)
iaas_ip_address_group_create_202 = (
    'You do not have permission to make this request. You can only create an IP Address Group for your own Member.'
)
# update
iaas_ip_address_group_update_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid IP Address Group record.'
)
iaas_ip_address_group_update_101 = (
    'The "name" parameter is invalid. "name" is required. "name" can only contain uppercase letters, lowercase letters,'
    'digits, a hypen (-) or an underscore (_) and the "name" must start with a letter.'
)
iaas_ip_address_group_update_102 = (
    'The "name" parameter is invalid. "name" is already in use for another IP Address Group within the Member.'
)
iaas_ip_address_group_update_103 = 'The "version" parameter is invalid. "version" must be an integer, 4 or 6.'
iaas_ip_address_group_update_104 = 'The "version" parameter is invalid. "version" must be 4 or 6.'
iaas_ip_address_group_update_105 = 'The "cidrs" parameter is invalid. "cidrs" is required and must be a list.'
iaas_ip_address_group_update_106 = (
    'The "cidrs" parameter is invalid. There must be at least one CIDR item in the "cidrs" list'
)
iaas_ip_address_group_update_107 = (
    'One of the items in the "cidrs" parameter is invalid. Each item must be a valid address.'
)
iaas_ip_address_group_update_108 = (
    'One of the items in the "cidrs" parameter is invalid. Each item must have the same network version as the version '
    'for this instance.'
)
iaas_ip_address_group_update_201 = (
    'You do not have permission to make this request. You can only update an IP Address Group owned your Member.'
)
# delete
iaas_ip_address_group_delete_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid IP Address Group record.'
)
iaas_ip_address_group_delete_201 = (
    'You do not have permission to make this request. You can only delete an IP Address Group owned your Member.'
)
