"""
Error Codes for all of the methods in the Server service
"""

# List
iaas_server_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
iaas_server_list_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can list Server records.'
)
# Create
iaas_server_create_101 = 'The "type_id" parameter is invalid. "type_id" is required.'
iaas_server_create_102 = 'The "type_id" parameter is invalid. "type_id" must be a valid integer.'
iaas_server_create_103 = 'The "type_id" parameter is invalid. "type_id" does not correspond with a valid ServerType.'
iaas_server_create_104 = 'The "asset_tag" parameter is invalid. "asset_tag" must be a valid integer.'
iaas_server_create_105 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_server_create_106 = 'The "model" parameter is invalid. "model" cannot be longer than 64 characters.'
iaas_server_create_107 = 'The "ram" parameter is invalid. "ram" is required.'
iaas_server_create_108 = 'The "ram" parameter is invalid. "ram" must be a valid integer.'
iaas_server_create_109 = 'The "ram" parameter is invalid. "ram" must be a positive integer.'
iaas_server_create_110 = 'The "cores" parameter is invalid. "cores" is required.'
iaas_server_create_111 = 'The "cores" parameter is invalid. "cores" must be a valid integer.'
iaas_server_create_112 = 'The "cores" parameter is invalid. "cores" must be a positive integer.'
iaas_server_create_113 = 'The "storage_type_id" parameter is invalid. "storage_type_id" is required.'
iaas_server_create_114 = 'The "storage_type_id" parameter is invalid. "storage_type_id" must be a valid integer.'
iaas_server_create_115 = (
    'The "storage_type_id" parameter is invalid. "storage_type_id" does not correspond with a valid StorageType.'
)
iaas_server_create_116 = 'The "gb" parameter is invalid. "gb" is required.'
iaas_server_create_117 = 'The "gb" parameter is invalid. "gb" must be a valid integer.'
iaas_server_create_118 = 'The "gb" parameter is invalid. "gb" cannot be less than 100 GB.'
iaas_server_create_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can create Server records.'
)

# Read
iaas_server_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Server record.'
iaas_server_read_201 = (
    'You do not have permission to make this request. You can only read Servers that belong to your address'
)

# Update
iaas_server_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Server record.'
iaas_server_update_101 = 'The "asset_tag" parameter is invalid. "asset_tag" must be a valid integer.'
iaas_server_update_102 = 'The "cores" parameter is invalid. "cores" must be a valid integer.'
iaas_server_update_103 = 'The "cores" parameter is invalid. "cores" must be a positive integer.'
iaas_server_update_104 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_server_update_105 = 'The "gb" parameter is invalid. "gb" must be a valid integer.'
iaas_server_update_106 = 'The "gb" parameter is invalid. "gb" cannot be less than 100 GB.'
iaas_server_update_107 = 'The "model" parameter is invalid. "model" cannot be longer than 64 characters.'
iaas_server_update_108 = 'The "ram" parameter is invalid. "ram" must be a valid integer.'
iaas_server_update_109 = 'The "ram" parameter is invalid. "ram" must be a positive integer.'
iaas_server_update_110 = 'The "storage_type_id" parameter is invalid. "storage_type_id" must be a valid integer.'
iaas_server_update_111 = (
    'The "storage_type_id" parameter is invalid. "storage_type_id" does not correspond with a valid StorageType.'
)
iaas_server_update_112 = 'The "type_id" parameter is invalid. "type_id" must be a valid integer.'
iaas_server_update_113 = 'The "type_id" parameter is invalid. "type_id" does not correspond with a valid ServerType.'

iaas_server_update_201 = (
    'You do not have permission to make this request. You can only update Servers that belong to your address'
)
