"""
Error Codes for all the Methods in the Ceph Service
"""

# List
iaas_ceph_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
iaas_ceph_create_101 = 'The "project_id" parameter is invalid. "project_id" is a required field.'
iaas_ceph_create_102 = 'The "project_id" parameter is invalid. "project_id" must be an integer.'
iaas_ceph_create_103 = (
    'The "project_id" parameter is invalid. "project_id" must identify a valid Project in your Address.'
)
iaas_ceph_create_104 = 'The "CEPH_001" parameter is invalid. "CEPH_001" is a required field.'
iaas_ceph_create_105 = 'The "CEPH_001" parameter is invalid. "CEPH_001" must be an integer.'
iaas_ceph_create_106 = 'The "CEPH_001" parameter is invalid. "CEPH_001" cannot be negative.'
iaas_ceph_create_107 = 'The "name" parameter is invalid. "name" is a required field.'
iaas_ceph_create_108 = (
    'The "name" parameter is invalid. "name" may only contain alphanumeric characters, hyphens, underscores, '
    'periods and spaces.'
)
iaas_ceph_create_109 = 'The "name" parameter is invalid. "name" must not exceed 128 characters.'
iaas_ceph_create_110 = (
    'The "name" parameter is invalid. There is already a Ceph drive with the same name in the specified Region.'
)
iaas_ceph_create_201 = (
    'You do not have permission to make this request. A User must be public to create Ceph drives.'
)
# Read
iaas_ceph_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Ceph record.'
iaas_ceph_read_201 = (
    'You do not have permission to make this request. Robot Users can only read Ceph objects in their own Region.'
)
iaas_ceph_read_202 = (
    'You do not have permission to make this request. Non-Global Active Users can only read Ceph objects that are in'
    'the same Address.'
)
iaas_ceph_read_203 = (
    'You do not have permission to make this request. Global Active Users can only read Ceph objects that are in'
    'the same Member.'
)

# Update
iaas_ceph_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Ceph record.'
iaas_ceph_update_002 = 'This request is invalid. Robot is only allowed to update the state of Ceph drives.'
iaas_ceph_update_101 = 'The "state" parameter is invalid. "state" must be an integer.'
iaas_ceph_update_102 = (
    'The "state" parameter is invalid. Your User cannot update the Ceph drive from its current state. Please check the'
    'API docs to see the full details of what state changes are allowed.'
)
iaas_ceph_update_103 = (
    'The "state" parameter is invalid. Moving the Ceph drive from the current to the requested state is not a valid '
    'state change. Please check the API docs to see the full details of what state changes are allowed.'
)
iaas_ceph_update_104 = 'The "CEPH_001" parameter is invalid. "CEPH_001" is a required field.'
iaas_ceph_update_105 = 'The "CEPH_001" parameter is invalid. "CEPH_001" must be an integer.'
iaas_ceph_update_106 = (
    'The "CEPH_001" parameter is invalid. "CEPH_001" must be greater than the current storage capacity of the Ceph '
    'drive.'
)
iaas_ceph_update_107 = (
    'Could not update the "CEPH_001" parameter. You may only update this value if your Ceph drive is currently '
    'RUNNING or QUIESCED.'
)
iaas_ceph_update_108 = (
    'Could not update the "CEPH_001" parameter. If updating the "state" parameter, you must set it to either '
    'RUNNING_UPDATE or QUIESCED_UPDATE to update the "CEPH_001" parameter.'
)
iaas_ceph_update_109 = 'The "name" parameter is invalid. "name" is a required field.'
iaas_ceph_update_110 = (
    'The "name" parameter is invalid. "name" may only contain alphanumeric characters, hyphens, underscores, '
    'periods and spaces.'
)
iaas_ceph_update_111 = 'The "name" parameter is invalid. "name" cannot be greater than 128 characters.'
iaas_ceph_update_112 = (
    'The "name" parameter is invalid. Your Address already owns a Ceph drive in this Region with the same name. '
)
iaas_ceph_update_201 = (
    'You do not have permission to make this request. A Ceph drive cannot be updated while it is attached to '
    'another resource.'
)
iaas_ceph_update_202 = (
    'You do not have permission to make this request. A Robot can only update Ceph drives in its region.'
)
iaas_ceph_update_203 = (
    'You do not have permission to make this request. You can only update Ceph drives that are in Projects that your '
    'Address owns.'
)
iaas_ceph_update_204 = (
    'You do not have permission to make this request. A User must be public to update Ceph drives.'
)
