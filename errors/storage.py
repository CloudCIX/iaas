"""
Error Codes for all of the methods in the Storage service
"""

# List
iaas_storage_list_001 = 'The "vm_id" parameter is invalid. "vm_id" does not correspond with a valid VM record.'
iaas_storage_list_002 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
iaas_storage_list_201 = (
    'You do not have permission to make this request. A global active user can only list Storage records for VMs in '
    'Addresses in their Member.'
)
iaas_storage_list_202 = (
    'You do not have permission to make this request. You can only list Storage records for VMs you own.'
)


# Create
iaas_storage_create_001 = 'The "vm_id" parameter is invalid. "vm_id" does not correspond with a valid VM record.'
iaas_storage_create_002 = (
    'The "vm_id" parameter is invalid. The chosen VM is not currently in a state where it can be updated. '
    'Please ensure it is in a valid updatable state before attempting to send this request again.'
)
iaas_storage_create_003 = (
    'The "primary" parameter is invalid. You cannot create a second "primary" Storage for an existing VM.'
)
iaas_storage_create_101 = 'The "gb" parameter is invalid. "gb" is required.'
iaas_storage_create_102 = 'The "gb" parameter is invalid. "gb" must be a valid integer.'
iaas_storage_create_103 = 'The "gb" parameter is invalid. "gb" must be within the range of 50 and 10,000 inclusive.'
iaas_storage_create_104 = 'The "name" parameter is invalid. "name" is required.'
iaas_storage_create_105 = 'The "name" parameter is invalid. "name" cannot be longer than 50 characters.'
iaas_storage_create_106 = 'The "primary" parameter is invalid. "primary" must be a valid boolean.'
iaas_storage_create_201 = (
    'You do not have permission to make this request. You can only create Storage records for VMs you own.'
)
iaas_storage_create_202 = 'You do not have permission to make this request. A User must be public to create Storages.'

# Read
iaas_storage_read_001 = 'The "vm_id" path parameter is invalid. "vm_id" does not correspond to a valid VM record.'
iaas_storage_read_002 = (
    'The "pk" path parameter is invalid. "pk" does not correspond to a valid Storage record in the specified VM.'
)
iaas_storage_read_201 = (
    'You do not have permission to make this request. Robots may only read Storages that are in their own region.'
)
iaas_storage_read_202 = (
    'You do not have permission to make this request. A global active user can only read Storages for VMs in Addresses '
    'in their Member.'
)
iaas_storage_read_203 = (
    'You do not have permission to make this request. Users can only read Storages that are in VMs in Projects that '
    'belong to their Address.'
)

# Update
iaas_storage_update_101 = 'The "gb" parameter is invalid. "gb" must be a valid integer.'
iaas_storage_update_102 = (
    'The "gb" parameter is invalid. "gb" cannot be higher than 10,000 or lower than its current value.'
)
iaas_storage_update_103 = 'The "name" parameter is invalid. "name" cannot be an empty string.'
iaas_storage_update_104 = 'The "name" parameter is invalid. "name" cannot be longer than 50 characters.'
