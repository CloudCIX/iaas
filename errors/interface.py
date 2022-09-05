"""
Error Codes for all of the methods in the Interface service
"""

# List
iaas_interface_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
iaas_interface_list_201 = (
    'You do not have permission to make this request. Only Users whose address is a region can list Interface records.'
)
# Create
iaas_interface_create_101 = 'The "server_id" parameter is invalid. "server_id" is required.'
iaas_interface_create_102 = 'The "server_id" parameter is invalid. "server_id" must be a valid integer.'
iaas_interface_create_103 = (
    'The "server_id" parameter is invalid. "server_id" does not correspond with a valid Server record.'
)
iaas_interface_create_104 = (
    'The "server_id" parameter is invalid. "server_id" does not correspond with a Server in your region.'
)
iaas_interface_create_105 = 'The "mac_address" parameter is invalid. "mac_address" is required.'
iaas_interface_create_106 = (
    'The "mac_address" parameter is invalid. "mac_address" is not a string containing valid MAC Address.'
)
iaas_interface_create_107 = (
    'The "ip_address" parameter is invalid. "ip_address" is not a string containing a valid IP Address.'
)
iaas_interface_create_108 = 'The "hostname" parameter is invalid. "hostname" cannot be longer than 64 characters.'
iaas_interface_create_109 = 'The "details" parameter is invalid. "details" cannot be longer than 64 characters.'
iaas_interface_create_110 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_interface_create_201 = (
    'You do not have permission to make this request. Users whose address is a region can create an Interface record.'
)
# Read
iaas_interface_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Interface record.'
iaas_interface_read_201 = (
    'You do not have permission to make this request. Robots may only read Interfaces that are in their own region.'
)

# Update
iaas_interface_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Interface record.'
iaas_interface_update_101 = 'The "details" parameter is invalid. "details" cannot be longer than 64 characters.'
iaas_interface_update_102 = 'The "enabled" parameter is invalid. "enabled" must be a valid boolean.'
iaas_interface_update_103 = 'The "hostname" parameter is invalid. "hostname" cannot be longer than 64 characters.'
iaas_interface_update_104 = (
    'The "ip_address" parameter is invalid. "ip_address" is not a string containing a valid IP Address.'
)
iaas_interface_update_105 = (
    'The "mac_address" parameter is invalid. "mac_address" is not a string containing valid MAC Address.'
)
iaas_interface_update_201 = (
    'You do not have permission to make this request. You can only update Interfaces for Servers that belong to your '
    'address'
)

# Delete
iaas_interface_delete_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Interface record.'
iaas_interface_delete_201 = (
    'You do not have permission to make this request. You can only delete Interfaces for Servers that belong to your '
    'address'
)
