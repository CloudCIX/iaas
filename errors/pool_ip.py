"""
Error Codes for all of the Methods in the PoolIP Service
"""

# List
iaas_pool_ip_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_pool_ip_create_101 = (
    'The "ip_address" parameter is invalid. "ip_address" is required and must be a string containing a valid IP '
    'address.'
)
iaas_pool_ip_create_102 = (
    'The "ip_address" parameter is invalid. "ip_address" is already in use by another PoolIP record.'
)
iaas_pool_ip_create_103 = (
    'The "ip_address" parameter is invalid. The address contained in "ip_address" is already in use by an IPAddress '
    'record.'
)
iaas_pool_ip_create_104 = 'The "domain" parameter is invalid. "domain" is required.'
iaas_pool_ip_create_105 = 'The "domain" parameter is invalid. "domain" cannot be longer than 240 characters.'
iaas_pool_ip_create_106 = (
    'The "domain" parameter is invalid. Each segment of "domain" separated by "." characters cannot be longer than 63 '
    'characters.'
)
iaas_pool_ip_create_107 = (
    'The "domain" parameter is invalid. "domain" must be a ".cloudcix.com" domain for PoolIP records.'
)
iaas_pool_ip_create_108 = 'The "domain" parameter is invalid. "domain" is already in use by another PoolIP record.'
iaas_pool_ip_create_201 = (
    'You do not have permission to make this request. Only Users in Member 1 can create PoolIP records.'
)

# Read
iaas_pool_ip_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid PoolIP record.'

# Update
iaas_pool_ip_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid PoolIP record.'
iaas_pool_ip_update_101 = (
    'The "ip_address" parameter is invalid. "ip_address" is required and must be a string containing a valid IP '
    'address.'
)
iaas_pool_ip_update_102 = (
    'The "ip_address" parameter is invalid. "ip_address" is already in use by another PoolIP record.'
)
iaas_pool_ip_update_103 = (
    'The "ip_address" parameter is invalid. The address contained in "ip_address" is already in use by an IPAddress '
    'record.'
)
iaas_pool_ip_update_104 = 'The "domain" parameter is invalid. "domain" is required.'
iaas_pool_ip_update_105 = 'The "domain" parameter is invalid. "domain" cannot be longer than 240 characters.'
iaas_pool_ip_update_106 = (
    'The "domain" parameter is invalid. Each segment of "domain" separated by "." characters cannot be longer than 63 '
    'characters.'
)
iaas_pool_ip_update_107 = (
    'The "domain" parameter is invalid. "domain" must be a ".cloudcix.com" domain for PoolIP records.'
)
iaas_pool_ip_update_108 = 'The "domain" parameter is invalid. "domain" is already in use by another PoolIP record.'
iaas_pool_ip_update_201 = (
    'You do not have permission to make this request. Only Users in Member 1 can update PoolIP records.'
)

# Delete
iaas_pool_ip_delete_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid PoolIP record.'
iaas_pool_ip_delete_201 = (
    'You do not have permission to make this request. Only Users in Member 1 can delete PoolIP records.'
)
