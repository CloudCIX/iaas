"""
Error Codes for all of the Methods in the Backup service
"""
# List
iaas_backup_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)
# create
iaas_backup_create_001 = (
    'A backup cannot be created as one or more backups of this VM are currently in a progress state. Please wait for '
    ' Robot to finish its work before requesting to create a new backup.'
)
iaas_backup_create_002 = (
    'A backup cannot be created as this VM has GPUs attached. Please update the VM by detatching the GPUs before '
    'requesting to create a new backup.'
)
iaas_backup_create_101 = 'The "vm_id" parameter is invalid. "vm_id" is required and must be an integer.'
iaas_backup_create_102 = 'The "vm_id" parameter is invalid. "vm_id" must belong to a valid VM record.'
iaas_backup_create_103 = (
    'The "vm_id" parameter is invalid. Backups can only be created of a VM that is in a RUNNING state.'
)
iaas_backup_create_104 = 'The "name" parameter is invalid. "name" is required and must be a string.'
iaas_backup_create_105 = 'The "name" parameter is invalid. "name" must be unique for the VM.'
iaas_backup_create_106 = (
    'The "repository" parameter is invalid. "repository" is required and must be an integer. "repository" represents '
    'the backup location, with the primary backup being "repository=1" and secondary backup being "repository=2".'
)
iaas_backup_create_107 = (
    'The "repository" parameter is invalid. "repository" must be an integer with value 1 or 2. "repository" represents '
    'the backup location, with the primary backup being "repository=1" and secondary backup being "repository=2".'
)

iaas_backup_create_201 = (
    'You do not have permission to make this request. You can only create Backups of a VM in your Address.'
)
iaas_backup_create_202 = (
    'You do not have permission to make this request. A User must be public to create Backups.'
)
# Reads
iaas_backup_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid backup record.'
iaas_backup_read_201 = (
    'You do not have permission to make this request. Robots can only read the Backups of a VM in their region.'
)
iaas_backup_read_202 = (
    'You do not have permission to make this request. A global active user can only read Backups of a VM for Addresses '
    'in their Member.'
)
iaas_backup_read_203 = (
    'You do not have permission to make this request. A user can only read Backups of a VM that they own.'
)
# update
iaas_backup_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Backup record.'
iaas_backup_update_002 = (
    'One or more backups of the VM are currently being scrubbed/updated. Please wait for Robot to finish working'
    ' before updating another Backup of the same VM.'
)
iaas_backup_update_101 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_backup_update_102 = 'The "name" parameter is invalid. "name" is already in use for another Backup of this VM.'
iaas_backup_update_103 = 'The "state" parameter is invalid. "state" must be an integer.'
iaas_backup_update_104 = (
    'The "state" parameter is invalid. The Backup cannot be updated out of its current state. Please wait for Robot to '
    'finish the current task it is running and try again.'
)
iaas_backup_update_105 = (
    'The "state" parameter is invalid. The requested state change is invalid. Please check the API docs to see the '
    'full details of what state changes are allowed.'
)
iaas_backup_update_106 = (
    'The "state" parameter is invalid. The Backup cannot be updated out of its current state. Please wait for Robot to '
    'finish whatever task it is running and try again.'
)
iaas_backup_update_107 = (
    'The "state" parameter is invalid. "state" parameter of Backup can only updated if the VM is in a RUNNING "state".'
)
iaas_backup_update_108 = (
    'The "time_valid" parameter is invalid. "time_valid" must be a date and time string in isoformat.'
)
iaas_backup_update_201 = (
    'You do not have permission to make this request. Robots can only update the Backups of a VM in their region.'
)
iaas_backup_update_202 = (
    'You do not have permission to make this request. You can only update Backups of a VMs in your Address.'
)
iaas_backup_update_203 = (
    'You do not have permission to make this request. A User must be public to update Backups.'
)
iaas_backup_update_204 = (
    'You do not have permission to make this request. The time_valid field can only be updated by Robot.'
)
