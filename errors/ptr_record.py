"""
Error Codes for all of the Methods in the Record Service
"""

# List
iaas_ptr_record_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_ptr_record_create_001 = (
    'An error occurred attempting to interact with the Rage4 API. CloudCIX have been notified, please try again later.'
)
iaas_ptr_record_create_002 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_ptr_record_create_003 = (
    'An error occurred attempting to interact with the Rage4 API. CloudCIX have been notified, please try again later.'
)
iaas_ptr_record_create_004 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_ptr_record_create_005 = (
    'An error occurred attempting to create the Record in the Rage4 API. CloudCIX have been notified, please try again '
    'later.'
)
iaas_ptr_record_create_006 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_ptr_record_create_101 = 'The "ip_address" parameter is invalid. "ip_address" is required.'
iaas_ptr_record_create_102 = (
    'The "ip_address" parameter is invalid. "ip_address" must be a string containing a valid IP address.'
)
iaas_ptr_record_create_103 = 'The "ip_address" parameter is invalid. "ip_address" must be a public IP address.'
iaas_ptr_record_create_104 = 'The "content" parameter is invalid. "content" is required.'
iaas_ptr_record_create_105 = 'The "content" parameter is invalid. "content" cannot be longer than 255 characters.'
iaas_ptr_record_create_106 = (
    'The "content" parameter is invalid. Each segment of "content" separated by "." characters cannot be longer than '
    '63 characters.'
)
iaas_ptr_record_create_107 = 'The "time_to_live" parameter is invalid. "time_to_live" must be a valid integer.'
iaas_ptr_record_create_108 = (
    'The "time_to_live" parameter is invalid. "time_to_live" cannot be less than 180 (3 minutes).'
)
iaas_ptr_record_create_201 = (
    'You do not have permission to make this request. Your Member must be self managed.'
)

# Read
iaas_ptr_record_read_001 = 'The "pk" path parameter is invalid. "pk" must correspond with a valid PTR Record record.'

# Update
iaas_ptr_record_update_001 = 'The "pk" path parameter is invalid. "pk" must correspond with a valid PTR Record record.'
iaas_ptr_record_update_002 = (
    'There was an error updating the Record in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_ptr_record_update_003 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_ptr_record_update_101 = 'The "content" parameter is invalid. "content" is required.'
iaas_ptr_record_update_102 = 'The "content" parameter is invalid. "content" cannot be longer than 255 characters.'
iaas_ptr_record_update_103 = (
    'The "content" parameter is invalid. Each segment of "content" separated by "." characters cannot be longer than '
    '63 characters.'
)
iaas_ptr_record_update_104 = 'The "time_to_live" parameter is invalid. "time_to_live" must be a valid integer.'
iaas_ptr_record_update_105 = (
    'The "time_to_live" parameter is invalid. "time_to_live" cannot be less than 180 (3 minutes).'
)
iaas_ptr_record_update_201 = 'You do not have permission to make this request. You do not own this Record.'

# Delete
iaas_ptr_record_delete_001 = 'The "pk" path parameter is invalid. "pk" must correspond with a valid PTR Record record.'
iaas_ptr_record_delete_002 = (
    'There was an error deleting the Record in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_ptr_record_delete_003 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_ptr_record_delete_201 = 'You do not have permission to make this request. You do not own this Record.'
