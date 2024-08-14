"""
Error Codes for all of the methods in the Project service
"""

# List
iaas_project_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_project_create_101 = 'The "region_id" parameter is invalid. "region_id" is required.'
iaas_project_create_102 = 'The "region_id" parameter is invalid. "region_id" must be a valid integer.'
iaas_project_create_103 = (
    'The "region_id" parameter is invalid. "region_id" must be the ID of a CloudCIX region Address that your Address is'
    ' linked to.'
)
iaas_project_create_104 = (
    'The "region_id" parameter is invalid. "region_id" does not correspond with a valid CloudCIX region that your '
    'Address has permission to build in.'
)
iaas_project_create_105 = 'The "name" parameter is invalid. "name" is required.'
iaas_project_create_106 = 'The "name" parameter is invalid. "name" cannot be longer than 100 characters.'
iaas_project_create_107 = 'The "name" parameter is invalid. Your Address already has a Project with the same name.'
iaas_project_create_108 = 'The "grace_period" parameter is invalid. "grace_period" cannot be less than value 0.'
iaas_project_create_109 = 'The "grace_period" parameter is invalid. "grace_period" must be a valid integer.'
iaas_project_create_201 = 'You do not have permission to make this request. Your Member must be self managed.'
iaas_project_create_202 = 'You do not have permission to make this request. A User must be public to create Projects.'

# Read
iaas_project_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Project record.'
iaas_project_read_201 = (
    'You do not have permission to make this request. Robots may only read Projects that are in their own region.'
)
iaas_project_read_202 = (
    'You do not have permission to make this request. A global active user can only read Projects for Addresses in '
    'their Member.'
)
iaas_project_read_203 = 'You do not have permission to make this request. You can only read Projects that you own.'

# Update
iaas_project_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Project record.'
iaas_project_update_101 = 'The "name" parameter is invalid. "name" is required.'
iaas_project_update_102 = 'The "name" parameter is invalid. "name" cannot be longer than 100 characters.'
iaas_project_update_103 = 'The "name" parameter is invalid. Your Address already has a Project with the same name.'
iaas_project_update_104 = (
    'The "state" parameter cannot be updated yet. Please wait until all your newly requested infrastructure has '
    'finished building before making requests to update the state of a Project as a whole.'
)
iaas_project_update_105 = 'The "state" parameter is invalid. "state" must be a valid integer.'
iaas_project_update_106 = 'The "state" parameter is invalid. "state" can only be Restore (4) or Scrub (8).'
iaas_project_update_107 = (
    'The "state" parameter is invalid. "state" can only be changed when all of the Project infrastructure is in '
    'stable states.'
)
iaas_project_update_108 = 'The "state" parameter is invalid. You can only Scrub a Project that is currently running.'
iaas_project_update_109 = (
    'The "state" parameter is invalid. One or more of the VMs in the Project has GPUs attached. Please detach all GPUs '
    'from the VMs before requesting to Scrub.'
)
iaas_project_update_110 = (
    'The "state" parameter is invalid. One or more of the VMs in the Project has running Snapshots. Please delete all '
    'Snapshots of the VMs before requesting to Scrub.'
)
iaas_project_update_111 = 'The "state" parameter is invalid. You can only Restore a Project that is currently Shutdown.'
iaas_project_update_112 = 'The "grace_period" parameter is invalid. "grace_period" cannot be less than value 0.'
iaas_project_update_113 = 'The "grace_period" parameter is invalid. "grace_period" must be a valid integer.'
iaas_project_update_201 = (
    'You do not have permission to make this request. Robots may only update Projects that are in their own region.'
)
iaas_project_update_202 = 'You do not have permission to make this request. You can only update Projects that you own.'
iaas_project_update_203 = 'You do not have permission to make this request. A User must be public to update Projects.'
