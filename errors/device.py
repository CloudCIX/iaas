"""
Error Codes for all Methods in the Device Service
"""
# List
iaas_device_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
# Create
iaas_device_create_101 = (
    'The "device_type_id" parameter is invalid. "device_type_id" is required and must be an integer.'
)
iaas_device_create_102 = 'The "device_type_id" parameter is invalid. "device_type_id" must be an integer.'
iaas_device_create_103 = (
    'The "device_type_id" parameter is invalid. "device_type_id" must correspond to a valid Device Type record in '
    'CloudCIX.'
)
iaas_device_create_104 = 'The "server_id" parameter is invalid. "server_id" is required and must be an integer.'
iaas_device_create_105 = 'The "server_id" parameter is invalid. "server_id" must be an integer.'
iaas_device_create_106 = (
    'The "server_id" parameter is invalid. "server_id" must correspond to a valid Server in your User\'s Region.'
)
iaas_device_create_107 = (
    'The "id_on_host" parameter is invalid. "id_on_host" is required and must be a string in the format XXXX:XX:XX.X '
    'where X represents a hexadecimal digit.'
)
iaas_device_create_108 = (
    'The "id_on_host" parameter is invalid. "id_on_host" must be a string in the format XXXX:XX:XX.X where X '
    'represents a hexadecimal digit.'
)
iaas_device_create_201 = (
    'You do not have permission to make this request. Only administrators in a Cloud Region can create Devices.'
)
# Read
iaas_device_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Device record.'
iaas_device_read_201 = (
    'You do not have permission to make this request. You can only read Devices for Servers that belong to your address'
)
# Update
iaas_device_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Device record.'
iaas_device_update_101 = (
    'The "device_type_id" parameter is invalid. "device_type_id" is required and must be an integer.'
)
iaas_device_update_102 = 'The "device_type_id" parameter is invalid. "device_type_id" must be an integer.'
iaas_device_update_103 = (
    'The "device_type_id" parameter is invalid. "device_type_id" must correspond to a valid Device Type record in '
    'CloudCIX.'
)
iaas_device_update_104 = (
    'The "id_on_host" parameter is invalid. "id_on_host" is required and must be a string in the format XXXX:XX:XX.X '
    'where X represents a hexadecimal digit.'
)
iaas_device_update_105 = (
    'The "id_on_host" parameter is invalid. "id_on_host" must be a string in the format XXXX:XX:XX.X where X '
    'represents a hexadecimal digit.'
)

iaas_device_update_106 = 'The "server_id" parameter is invalid. "server_id" is required and must be an integer.'
iaas_device_update_107 = 'The "server_id" parameter is invalid. "server_id" must be an integer.'
iaas_device_update_108 = (
    'The "server_id" parameter is invalid. "server_id" must correspond to a valid Server in your User\'s Region.'
)
iaas_device_update_109 = 'The "vm_id" parameter is invalid. Robot can only reset "vm_id" to None.'
iaas_device_update_201 = (
    'You do not have permission to make this request. A Device cannot be updated while connected to a VM.'
)
