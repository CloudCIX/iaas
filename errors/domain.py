"""
Error Codes for all of the Methods in the Domain Service
"""

# List
iaas_domain_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_domain_create_001 = (
    'There was an error creating the Domain in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_domain_create_002 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_domain_create_101 = 'The "name" parameter is invalid. "name" is required and must be a string.'
iaas_domain_create_102 = 'The "name" parameter is invalid. "name" cannot be longer than 240 characters.'
iaas_domain_create_103 = (
    'The "name" parameter is invalid. Each segment of "name" separated by "." characters cannot be longer than 63 '
    'characters.'
)
iaas_domain_create_201 = (
    'You do not have permission to make this request. Your Member must be self managed.'
)

# Read
iaas_domain_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Domain record.'
iaas_domain_read_201 = 'You do not have permission to make this request. You do not own this domain.'

# Delete
iaas_domain_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Domain record.'
iaas_domain_delete_002 = (
    'There was an error deleting the Domain in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_domain_delete_003 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_domain_delete_201 = 'You do not have permission to make this request. You do not own this domain.'
