"""
Error Codes for all of the Methods in the CIXBlacklist Service
"""

# List
iaas_cix_blacklist_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_cix_blacklist_create_101 = 'The "cidr" parameter is invalid. "cidr" is required and must be a valid address.'
iaas_cix_blacklist_create_102 = 'The "cidr" parameter is invalid. A record with that "cidr" already exists.'
iaas_cix_blacklist_create_201 = 'You do not have permission to make this request. You must be a user in Member 1.'

# Read
iaas_cix_blacklist_read_001 = 'The "cidr" path parameter is invalid. "cidr" must belong to a valid CIXBlacklist record.'

# Update
iaas_cix_blacklist_update_001 = (
    'The "cidr" path parameter is invalid. "cidr" must belong to a valid CIXBlacklist record.'
)
iaas_cix_blacklist_update_101 = 'The "cidr" parameter is invalid. "cidr" is required and must be a valid address.'
iaas_cix_blacklist_update_102 = 'The "cidr" parameter is invalid. A record with that "cidr" already exists.'
iaas_cix_blacklist_update_201 = 'You do not have permission to make this request. You must be a user in Member 1.'

# Delete
iaas_cix_blacklist_delete_001 = (
    'The "cidr" path parameter is invalid. "cidr" must belong to a valid CIXBlacklist record.'
)
iaas_cix_blacklist_delete_201 = 'You do not have permission to make this request. You must be a user in Member 1.'
