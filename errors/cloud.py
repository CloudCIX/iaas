"""
Errors for Cloud services
"""

# Create
iaas_cloud_create_101 = 'The "project" parameter is invalid. "project" is required.'
iaas_cloud_create_102 = 'The "project" parameter is invalid. "project" must be a dictionary.'
iaas_cloud_create_103 = (
    'There was an error creating your cloud Subnet. CloudCIX has hit an internal capacity limit. Our team have been '
    'notified.'
)
iaas_cloud_create_104 = 'The "vms" parameter is invalid. "vms" must be a list.'
iaas_cloud_create_105 = 'The "vms" parameter is invalid. "vms" is required and must be a non empty list.'
iaas_cloud_create_106 = 'The "vms" parameter is invalid. "vms" must be a list of dictionaries with data to create a VM.'
iaas_cloud_create_107 = 'The "firewall_rules" parameter is invalid. "firewall_rules" must be a list.'
iaas_cloud_create_108 = (
    'The "firewall_rules" parameter is invalid. "firewall_rules" must be a list of dictionaries with data to create a '
    'FirewallRule.'
)
iaas_cloud_create_201 = 'You do not have permission to make this request. Robot users cannot exeucte this request.'
iaas_cloud_create_202 = 'You do not have permission to make this request. Your Member must be self managed.'
iaas_cloud_create_203 = (
    'You do not have permission to make this request. A User must be public to create Cloud infrastructure.'
)

# Read
iaas_cloud_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Project record.'
iaas_cloud_read_201 = (
    'You do not have permission to make this request. A global active user can only read Projects for Addresses in '
    'their Member.'
)
iaas_cloud_read_202 = 'You do not have permission to make this request. You can only read Projects that you own.'

# Update
iaas_cloud_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid Project record.'
iaas_cloud_update_002 = (
    'This Project cannot currently be updated. The VirtualRouter is not in a state that can be updated. Please wait or '
    'contact CloudCIX Support if this persists.'
)
iaas_cloud_update_003 = (
    'This Project cannot currently be updated. One or more VMs are not in a state that can be updated. Please wait or '
    'contact CloudCIX Support if this persists.'
)
iaas_cloud_update_101 = 'The "project" parameter is invalid. "project" is required.'
iaas_cloud_update_102 = 'The "project" parameter is invalid. "project" must be a dictionary.'
iaas_cloud_update_103 = (
    'There was an error creating your cloud Subnet. CloudCIX has hit an internal capacity limit. Our team have been '
    'notified.'
)
iaas_cloud_update_104 = 'The "vms" parameter is invalid. "vms" must be a list.'
iaas_cloud_update_105 = 'The "vms" parameter is invalid. "vms" is required and must be a non empty list.'
iaas_cloud_update_106 = 'The "vms" parameter is invalid. "vms" must be a list of dictionaries with data to update a VM.'
iaas_cloud_update_107 = 'The "firewall_rules" parameter is invalid. "firewall_rules" must be a list.'
iaas_cloud_update_108 = (
    'The "firewall_rules" parameter is invalid. "firewall_rules" must be a list of dictionaries with data to create a '
    'FirewallRule.'
)
iaas_cloud_update_109 = 'This vm is invalid. The "id" field does not correspond with a valid VM record.'
iaas_cloud_update_201 = 'You do not have permission to make this request. Robot users cannot exeucte this request.'
iaas_cloud_update_202 = 'You do not have permission to make this request. You can only update Projects that you own.'
iaas_cloud_update_203 = (
    'You do not have permission to make this request. A User must be public to update Cloud infrastructure.'
)
