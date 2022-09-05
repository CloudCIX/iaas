"""
Error Codes for all of the Methods in the Record Service
"""

# List
iaas_record_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_record_create_001 = (
    'There was an error creating the Record in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_record_create_002 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_record_create_101 = 'The "domain_id" parameter is invalid. "domain_id" is required.'
iaas_record_create_102 = 'The "domain_id" parameter is invalid. "domain_id" must be a valid integer.'
iaas_record_create_103 = (
    'The "domain_id" parameter is invalid. "domain_id" does not correspond with a valid Domain record.'
)
iaas_record_create_104 = 'The "domain_id" parameter is invalid. The chosen Domain record is not owned by your Member.'
iaas_record_create_105 = 'The "type" parameter is invalid. "type" is required.'
iaas_record_create_106 = 'The "type" parameter is invalid. "type" must be one of the valid choice options.'
iaas_record_create_107 = (
    'The "type" parameter is invalid. "type" cannot be PTR for this view. Please use the `/ptr_record/` view to '
    'create PTR records instead.'
)
iaas_record_create_108 = 'The "name" parameter is invalid. "name" is required.'
iaas_record_create_109 = 'The "name" parameter is invalid. "name" cannot be longer than 80 characters.'
iaas_record_create_110 = 'The "content" parameter is invalid. "content" is required.'
iaas_record_create_111 = 'The "content" parameter is invalid. "content" cannot be longer than 255 characters.'
iaas_record_create_112 = 'The "time_to_live" parameter is invalid. "time_to_live" must be a valid integer.'
iaas_record_create_113 = 'The "time_to_live" parameter is invalid. "time_to_live" cannot be less than 180 (3 minutes).'
iaas_record_create_114 = 'The "priority" parameter is invalid. "priority" must be a valid integer.'
iaas_record_create_115 = 'The "priority" parameter is invalid. "priority" must be between 1 and 65535.'
iaas_record_create_116 = 'The "failover" parameter is invalid. "failover" must be a valid boolean value.'
iaas_record_create_117 = (
    'The "failover_content" parameter is invalid. "failover_content" cannot be longer than 255 characters.'
)
iaas_record_create_201 = 'You do not have permission to make this request. You do not own this Record.'

# Read
iaas_record_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Record record.'
iaas_record_read_201 = 'You do not have permission to make this request. Only Users who own the Record can read it.'

# Update
iaas_record_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Record record.'
iaas_record_update_002 = (
    'There was an error updating the Record in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_record_update_003 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_record_update_101 = 'The "domain_id" parameter is invalid. "domain_id" is required.'
iaas_record_update_102 = 'The "domain_id" parameter is invalid. "domain_id" must be a valid integer.'
iaas_record_update_103 = (
    'The "domain_id" parameter is invalid. "domain_id" does not correspond with a valid Domain record.'
)
iaas_record_update_104 = 'The "domain_id" parameter is invalid. The chosen Domain record is not owned by your Member.'
iaas_record_update_105 = 'The "name" parameter is invalid. "name" is required.'
iaas_record_update_106 = 'The "name" parameter is invalid. "name" cannot be longer than 80 characters.'
iaas_record_update_107 = 'The "content" parameter is invalid. "content" is required.'
iaas_record_update_108 = 'The "content" parameter is invalid. "content" cannot be longer than 255 characters.'
iaas_record_update_109 = 'The "time_to_live" parameter is invalid. "time_to_live" must be a valid integer.'
iaas_record_update_110 = 'The "time_to_live" parameter is invalid. "time_to_live" cannot be less than 180 (3 minutes).'
iaas_record_update_111 = 'The "priority" parameter is invalid. "priority" must be a valid integer.'
iaas_record_update_112 = 'The "priority" parameter is invalid. "priority" must be between 1 and 65535.'
iaas_record_update_113 = 'The "failover" parameter is invalid. "failover" must be a valid boolean value.'
iaas_record_update_114 = (
    'The "failover_content" parameter is invalid. "failover_content" cannot be longer than 255 characters.'
)
iaas_record_update_201 = 'You do not have permission to make this request. Only Users who own the Record can update it.'

# Delete
iaas_record_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Record record.'
iaas_record_delete_002 = (
    'There was an error deleting the Record in the Rage4 API. Please try again later or contact CloudCIX support if '
    'this persists.'
)
iaas_record_delete_003 = (
    'An unknown error has occurred in the Rage4 API. CloudCIX support has been notified, please try again later.'
)
iaas_record_delete_201 = 'You do not have permission to make this request. You do not own this Record.'
