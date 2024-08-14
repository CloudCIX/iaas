"""
Error Codes for all of the methods in the Snapshot service
"""

# List
iaas_snapshot_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Reads
iaas_snapshot_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Snapshot record.'
iaas_snapshot_read_201 = (
    'You do not have permission to make this request. Robots can only read the Snapshots of a VM in their region.'
)
iaas_snapshot_read_202 = (
    'You do not have permission to make this request. A global active user can only read Snapshots of a VM for '
    'Addresses in their Member.'
)
iaas_snapshot_read_203 = (
    'You do not have permission to make this request. Can only read Snapshots of a VM that you own.'
)
# Create
iaas_snapshot_create_001 = (
    'A Snapshot cannot be created as one or more snapshots of this VM are currently being scrubbed. Please wait for '
    'Robot to finish scrubbing Snapshots before requesting to create a new Snapshot.'
)
iaas_snapshot_create_002 = (
    'A Snapshot cannot be created as this VM has GPUs attached. Please update the VM by detatching the GPUs before '
    'requesting to create a new Snapshot.'
)
iaas_snapshot_create_101 = 'The "vm_id" parameter is invalid. "vm_id" is required and must be an integer.'
iaas_snapshot_create_102 = 'The "vm_id" parameter is invalid. "vm_id" must belong to a valid vm record.'
iaas_snapshot_create_103 = (
    'The "vm_id" parameter is invalid. Snapshots can only be created of a VM that is in a RUNNING state.'
)
iaas_snapshot_create_104 = 'The "vm_id" parameter is invalid. The VM specified contains more than one active snapshot.'
iaas_snapshot_create_105 = (
    'The "vm_id" parameter is invalid. The specified VM has no active snapshot in a RUNNING state. To create a new '
    'snapshot, the current active snapshot of the VM must be in a RUNNING state.'
)
iaas_snapshot_create_106 = 'The "name" parameter is invalid. "name" is required and must be a string.'
iaas_snapshot_create_107 = 'The "name" parameter is invalid. "name" must be unique for the VM.'
iaas_snapshot_create_201 = (
    'You do not have permission to make this request. You can only create Snapshots of a VM in your Address.'
)
iaas_snapshot_create_202 = (
    'You do not have permission to make this request. A User must be public to create Snapshots.'
)
# Update
iaas_snapshot_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Snapshot record.'
iaas_snapshot_update_002 = (
    'One or more snapshots of the VM are not in a Stable state. Please wait for Robot to finish scrubbing or '
    'building the snapshots before updating another of the same VM.'
)
iaas_snapshot_update_003 = (
    'A Snapshot cannot be updated as this VM has GPUs attached. Please update the VM by detatching the GPUs before '
    'requesting to update this Snapshot.'
)
iaas_snapshot_update_101 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_snapshot_update_102 = 'The "name" parameter is invalid. "name" is already in use for another Snapshot of this VM.'
iaas_snapshot_update_103 = 'The "state" parameter is invalid. "state" must be an integer.'
iaas_snapshot_update_104 = 'The "state" parameter is invalid. "state" must be within the range of 1 to 17 inclusive.'
iaas_snapshot_update_105 = (
    'The "state" parameter is invalid. The requested state change is invalid. Please check the API docs to see the '
    'full details of what state changes are allowed.'
)
iaas_snapshot_update_106 = (
    'The "state" parameter is invalid. The Snapshot cannot be updated out of its current state. Please wait for '
    'Robot to finish the current task it is running and try again.'
)
iaas_snapshot_update_107 = (
    'The "state" parameter is invalid. "state" parameter of Snapshot can only updated if the VM is in a '
    'RUNNING state".'
)
iaas_snapshot_update_108 = 'The "remove_subtree" property is invalid. "remove_subtree" must be a boolean.'
iaas_snapshot_update_109 = (
    'The "remove_subtree parameter is invalid. The "state" parameter must also be included.'
)
iaas_snapshot_update_110 = (
    'The "remove_subtree" parameter is invalid. "remove_subtree" can only included if '
    'the "state" parameter is set to state "SCRUB"'
)
iaas_snapshot_update_201 = (
    'You do not have permission to make this request. Robots can only read the Snapshots of a VM in their region.'
)
iaas_snapshot_update_202 = (
    'You do not have permission to make this request. You can only update Snapshots of a VMs in your Address.'
)
iaas_snapshot_update_203 = (
    'You do not have permission to make this request. A User must be public to update Snapshots.'
)

# Snapshot Tree
iaas_snapshot_tree_read_001 = (
    'The "vm_id" path parameter is invalid. "vm_id" does not correspond with a valid VM record.'
)
iaas_snapshot_tree_read_201 = (
    'You do not have permission to make this request. A global active user can only read a Snapshot Trees  of a VM for '
    'an Address in their Member.'
)
iaas_snapshot_tree_read_202 = (
    'You do not have permission to make this request. Can only read a Snapshot Tree of a VM that you own.'
)
