"""
Error Codes for all of the methods in the VM service
"""

# List
iaas_vm_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_vm_create_101 = 'The "project_id" parameter is invalid. "project_id" is required.'
iaas_vm_create_102 = 'The "project_id" parameter is invalid. "project_id" must be a valid integer.'
iaas_vm_create_103 = (
    'The "project_id" parameter is invalid. "project_id" does not correspond with a valid Project record.'
)
iaas_vm_create_104 = (
    'The "project_id" parameter is invalid. "project_id" does not correspond with a Project owned by your Address.'
)
iaas_vm_create_105 = 'The "image_id" parameter is invalid. "image_id" is required.'
iaas_vm_create_106 = 'The "image_id" parameter is invalid. "image_id" must be a valid integer.'
iaas_vm_create_107 = 'The "image_id" parameter is invalid. "image_id" does not correspond with a valid Image record.'
iaas_vm_create_108 = (
    'The "image_id" parameter is invalid. "image_id" does correspond with an Image in the region for the Project.'
)
iaas_vm_create_109 = 'The "storage_type_id" parameter is invalid. "storage_type_id" is required.'
iaas_vm_create_110 = 'The "storage_type_id" parameter is invalid. "storage_type_id" must be a valid integer.'
iaas_vm_create_111 = (
    'The "storage_type_id" parameter is invalid. "storage_type_id" does not correspond with a valid StorageType.'
)
iaas_vm_create_112 = 'The "storages" parameter is invalid. "storages" is required and must be a list.'
iaas_vm_create_113 = 'The "storages" parameter is invalid. "storages" cannot be empty.'
iaas_vm_create_114 = 'This storage entry is invalid. Each entry in "storages" must be an object.'
iaas_vm_create_115 = 'The "storages" parameter is invalid. Only one of the "storages" can be set to primary.'
iaas_vm_create_116 = (
    'The "storages" parameter is invalid. For Windows OS VMs, the minimum size of the primary drive is 32GB.'
)
iaas_vm_create_117 = 'The "cpu" parameter is invalid. "cpu" is required.'
iaas_vm_create_118 = 'The "cpu" parameter is invalid. "cpu" must be a valid integer.'
iaas_vm_create_119 = 'The "cpu" parameter is invalid. "cpu" must be greater than zero.'
iaas_vm_create_120 = 'The "ram" parameter is invalid. "ram" is required.'
iaas_vm_create_121 = 'The "ram" parameter is invalid. "ram" must be a valid integer.'
iaas_vm_create_122 = 'The "ram" parameter is invalid. "ram" must greater than zero.'
iaas_vm_create_123 = 'We were unable to find a Server to host this VM. Please contact CloudCIX Support.'
iaas_vm_create_124 = 'The "dns" parameter is invalid. "dns" is required.'
iaas_vm_create_125 = (
    'The "dns" parameter is invalid. "dns" must be a string containing valid IP Addresses, separated by commas.'
)
iaas_vm_create_126 = 'The "name" parameter is invalid. "name" is required.'
iaas_vm_create_127 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_vm_create_128 = 'The "name" parameter is invalid. "name" is already in use for another VM within this Project.'
iaas_vm_create_129 = 'Invalid public_key field, public_key must be of recommended SSH public key type.'
iaas_vm_create_130 = (
    'The `gateway_subnet` parameter is invalid. `gateway_subnet` is required and must be a valid address range.'
)
iaas_vm_create_131 = (
    'The "gateway_subnet" parameter is invalid. "gateway_subnet" does not correspond to any valid Subnet.'
)
iaas_vm_create_132 = (
    'The "ip_addresses" parameter is invalid. "ip_addresses" must be a list of dictionaries in the format of '
    '[{"address": "1.1.1.1", "nat": True}]'
)
iaas_vm_create_133 = 'The "ip_addresses" parameter is invalid. "ip_addresses" is required and cannot be an empty list.'
iaas_vm_create_134 = 'The "ip_addresses" parameter is invalid.  All IPs in the list must be unique.'
iaas_vm_create_135 = (
    'The "ip_addresses" parameter is invalid. The "image" selected does not supports multiple IP Addresses.'
)
iaas_vm_create_136 = 'The "ip_addresses" parameter is invalid. All IPs in the list  must be a valid IP Address.'
iaas_vm_create_137 = 'The "ip_addresses" parameter is invalid. All IPs in the list must be a private IP Address.'
iaas_vm_create_138 = (
    'The "ip_addresses" parameter is invalid. A VM IP address cannot be the network, gateway or broadcast address of '
    'its Subnet.'
)
iaas_vm_create_139 = (
    'The "ip_addresses" parameter is invalid. An IP Address with one of the specified ips already exists.'
)
iaas_vm_create_140 = (
    'The "ip_addresses" parameter is invalid. One of the supplied IPs is not from a Subnet in your VMs project'
)
iaas_vm_create_141 = (
    'The `ip_addresses` parameter is invalid.  You can only NAT IPs from the "gateway_subnet" of the VM.'
)
iaas_vm_create_142 = (
    'There was an issue generating a public IPAddress. There are no more public IP Addresses available in this region.'
    ' CloudCIX have been alerted to this situation and will remedy it as soon as possible, please try again later.'
)
iaas_vm_create_143 = (
    'The `userdata` parameter is invalid. The chosen OS image does not support userdata for Cloud Init.'
)
iaas_vm_create_144 = 'The `userdata` parameter is invalid. `userdata` must not exceed 16 KB in size.'
iaas_vm_create_145 = (
    'The `userdata` parameter is invalid. `userdata` must be one of the file formats allowed by Cloud Init. The full '
    'list of formats can be found at this url: https://cloudinit.readthedocs.io/en/latest/topics/format.html'
)

iaas_vm_create_201 = 'You do not have permission to make this request. A User must be public to create VMs.'

# Read
iaas_vm_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid VM record.'
iaas_vm_read_201 = 'You do not have permission to make this request. Robots can only read the VMs in their region.'
iaas_vm_read_202 = (
    'You do not have permission to make this request. A global active user can only read VMs that are owned by '
    'Addresses in their Member.'
)
iaas_vm_read_203 = 'You do not have permission to make this request. Can only read VMs that you own.'

# Update
iaas_vm_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid VM record.'
iaas_vm_update_101 = 'The "name" parameter is invalid. "name" is required.'
iaas_vm_update_102 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_vm_update_103 = 'The "name" parameter is invalid. "name" is already in use for another VM within this Project.'
iaas_vm_update_104 = 'The "state" parameter is invalid. "state" must be a valid integer.'
iaas_vm_update_105 = 'The "state" parameter is invalid. "state" must be within the range of 1 to 17 inclusive.'
iaas_vm_update_106 = (
    'The "state" parameter is invalid. The requested state change is invalid. Please check the API docs to see the '
    'full details of what state changes are allowed.'
)
iaas_vm_update_107 = (
    'The "state" parameter is invalid. It is not valid to change from the current state to the requested state. Please '
    'check the API docs to see the full details of what state changes are allowed.'
)
iaas_vm_update_108 = (
    'The "state" parameter is invalid. A VM can only be scrubbed if all GPUs are detached Please detach GPUs from VM '
    'before requesting to scrub.'
)
iaas_vm_update_109 = (
    'The "state" parameter is invalid. A VM can only be scrubbed if there are no active snapshots. Please delete all  '
    'snapshots of the VM before requesting to scrub.'
)
iaas_vm_update_110 = (
    'The "state" parameter is invalid. All snapshots must be in a stable state before state of the VM can be changed. '
    'A stable state for a Snapshot is RUNNING.'
)
iaas_vm_update_111 = (
    'The "ip_addresses" parameter is invalid. "ip_addresses" must be a list of dictionaries in the format of '
    '[{"ipAddress": "1.1.1.1", "nat": True}]'
)
iaas_vm_update_112 = 'The "ip_addresses" parameter is invalid. "ip_addresses" is required and cannot be an empty list.'
iaas_vm_update_113 = (
    'The `ip_addresses` parameter is invalid.  You can only NAT IPs from the "gateway_subnet" of the VM.'
)
iaas_vm_update_114 = (
    'There was an issue generating a public IPAddress. There are no more public IP Addresses available in this region.'
    ' CloudCIX have been alerted to this situation and will remedy it as soon as possible, please try again later.'
)
iaas_vm_update_115 = 'The "ip_addresses" parameter is invalid.  One of the supplied IPs in the list does not exist.'
iaas_vm_update_116 = 'The "cpu" parameter is invalid. "cpu" must be a valid integer.'
iaas_vm_update_117 = 'The "cpu" parameter is invalid. "cpu" must greater than zero.'
iaas_vm_update_118 = (
    'Could not update the "cpu" parameter. You may only update this value if your VM is currently RUNNING or QUIESCED.'
)
iaas_vm_update_119 = (
    'Could not update the "cpu" parameter. If updating the "state" parameter, you must set it to either RUNNING_UPDATE'
    ' or QUIESCED_UPDATE to update the "cpu" parameter.'
)
iaas_vm_update_120 = (
    'This update request cannot be fulfilled. The requested "cpu" increase is unavailable on the vm\'s host. Please '
    'contact CloudCIX to discuss possible solutions.'
)
iaas_vm_update_121 = 'The "ram" parameter is invalid. "ram" must be a valid integer.'
iaas_vm_update_122 = 'The "ram" parameter is invalid. "ram" must greater than zero.'
iaas_vm_update_123 = (
    'Could not update the "ram" parameter. You may only update this value if your VM is currently RUNNING or QUIESCED.'
)
iaas_vm_update_124 = (
    'Could not update the "ram" parameter. If updating the "state" parameter, you must set it to either RUNNING_UPDATE'
    ' or QUIESCED_UPDATE to update the "ram" parameter.'
)
iaas_vm_update_125 = (
    'This update request cannot be fulfilled. The requested "ram" increase is unavailable on the vm\'s host. Please '
    'contact CloudCIX to discuss possible solutions.'
)
iaas_vm_update_126 = 'The "storages" parameter is invalid. "storages" must be a list.'
iaas_vm_update_127 = 'This "storage" is invalid. Items in "storages" must be objects / dictionaries.'
iaas_vm_update_128 = (
    'This "storage" is invalid. As part of the VM update request, you cannot create new primary "storage" records.'
)
iaas_vm_update_129 = 'This "storage" is invalid. The given "id" does not correspond with an existing Storage record.'
iaas_vm_update_130 = (
    'This update request cannot be fulfilled. The requested "storages" increase(s) are unavailable on the vm\'s host. '
    'Please contact CloudCIX to discuss possible solutions.'
)
iaas_vm_update_131 = (
    'Could not update the "storages" parameter. You may only update this if your VM is currently RUNNING or QUIESCED.'
)
iaas_vm_update_132 = (
    'Could not update the "storages". If updating the "state" parameter, you must set it to either RUNNING_UPDATE'
    ' or QUIESCED_UPDATE to update the "storages".'
)
iaas_vm_update_133 = (
    'The `userdata` parameter is invalid. The chosen OS image does not support userdata for Cloud Init.'
)
iaas_vm_update_134 = 'The `userdata` parameter is invalid. `userdata` must not exceed 16 KB in size'
iaas_vm_update_135 = (
    'The `userdata` parameter is invalid. `userdata` must be one of the file formats allowed by Cloud Init. The full '
    'list of formats can be found at this url: https://cloudinit.readthedocs.io/en/latest/topics/format.html'
)
iaas_vm_update_136 = 'The "gpu" parameter is invalid. "gpu" must be a valid integer.'
iaas_vm_update_137 = (
    'This update request cannot be fulfilled. The requested "gpu" increase is unavailable as your VM is on a host that '
    'does not support GPUs. Please contact CloudCIX to discuss possible solutions.'
)
iaas_vm_update_138 = (
    'Could not update the "gpu" parameter. You may only update this value if your VM is currently RUNNING or QUIESCED.'
)
iaas_vm_update_139 = (
    'Could not update the "gpu" parameter. If updating the "state" parameter, you must set it to either RUNNING_UPDATE'
    ' or QUIESCED_UPDATE to update the "gpu" parameter.'
)
iaas_vm_update_140 = (
    'This update request cannot be fulfilled. The requested "gpu" increase is unavailable as all GPUs devices are '
    'currently in use. Please contact CloudCIX to discuss possible solutions.'
)
iaas_vm_update_201 = (
    'You do not have permission to make this request. Robots may only update VMs that are in their own region.'
)
iaas_vm_update_202 = (
    'You do not have permission to make this request. Users can only update VMs that are related to Projects that '
    'belong to their Address.'
)
iaas_vm_update_203 = 'You do not have permission to make this request. A User must be public to update VMs.'
