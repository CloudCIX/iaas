"""
Error Codes for all of the Methods in the Subnet Service
"""

# List
iaas_subnet_list_001 = (
    'There was an error fetching non self managed partner Addresses. Please try again later or contact '
    'developers@cloudcix.com if this persists.'
)
iaas_subnet_list_002 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_subnet_create_101 = 'The "address_id" parameter is invalid. "address_id" is required.'
iaas_subnet_create_102 = 'The "address_id" parameter is invalid. "address_id" must be a valid integer.'
iaas_subnet_create_103 = (
    'The "address_id" parameter is invalid. "address_id" must be the ID of your Address or an Address you are linked '
    'to.'
)
iaas_subnet_create_104 = 'The "allocation_id" parameter is invalid. "allocation_id" must be a valid integer.'
iaas_subnet_create_105 = (
    'The "allocation_id" parameter is invalid. "allocation_id" does not correspond with an Allocation record in an ASN '
    'owned by your Member.'
)
iaas_subnet_create_106 = 'The "parent_id" parameter is invalid. "parent_id" must be a valid integer.'
iaas_subnet_create_107 = (
    'The "parent_id" parameter is invalid. "parent_id" does not correspond with a valid Subnet record.'
)
iaas_subnet_create_108 = (
    'The "parent_id" parameter is invalid. "parent_id" does not correspond with a Subnet record in the '
    'chosen Allocation.'
)
iaas_subnet_create_109 = (
    'The "parent_id" parameter is invalid. "parent_id" must correspond with a Subnet record owned by '
    'your Address or a linked Address.'
)
iaas_subnet_create_110 = 'The "address_range" parameter is invalid. "address_range" is required.'
iaas_subnet_create_111 = (
    'The "address_range" parameter is invalid. "address_range" must be a string containing a valid Subnet.'
)
iaas_subnet_create_112 = (
    'The "address_range" parameter is invalid. "address_range" requires at least one of either "allocation_id" or '
    '"parent_id" to be sent and valid. Ensure that you send exactly one of these two fields.'
)
iaas_subnet_create_113 = (
    'The "address_range" parameter is invalid. "address_range" does not use the same IP version as the address range '
    'of the chosen Allocation.'
)
iaas_subnet_create_114 = (
    'The "address_range" parameter is invalid. "address_range" is not a subnet within the address range of the chosen '
    'Allocation.'
)
iaas_subnet_create_115 = (
    'The "address_range" parameter is invalid. A Subnet with the chosen "address_range" already exists in the chosen '
    'Allocation.'
)
iaas_subnet_create_116 = (
    'The "address_range" parameter is invalid. The sent "address_range" overlaps with a Subnet already in the chosen '
    'Allocation.'
)
iaas_subnet_create_117 = (
    'The "address_range" parameter is invalid. "address_range" does not use the same IP version as the address range '
    'of the chosen parent Subnet.'
)
iaas_subnet_create_118 = (
    'The "address_range" parameter is invalid. "address_range" cannot be the same address_range as the address_range '
    'of the chosen parent Subnet.'
)
iaas_subnet_create_119 = (
    'The "address_range" parameter is invalid. "address_range" is not a subnet within the address range of the chosen '
    'parent Subnet.'
)
iaas_subnet_create_120 = (
    'The "address_range" parameter is invalid. A Subnet with the chosen "address_range" already exists in the chosen '
    'parent Subnet.'
)
iaas_subnet_create_121 = (
    'The "address_range" parameter is invalid. The sent "address_range" overlaps with a Subnet already in the chosen '
    'parent Subnet.'
)
iaas_subnet_create_122 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_subnet_create_123 = 'The "vlan" parameter is invalid. "vlan" must be a valid integer.'
iaas_subnet_create_124 = (
    'The "vlan" parameter is invalid. "vlan" must be greater than or equal to 0, and less than 4095.'
)
iaas_subnet_create_125 = 'The "vxlan" parameter is invalid. "vxlan" must be a valid integer.'
iaas_subnet_create_126 = (
    'The "vxlan" parameter is invalid. "vxlan" must be greater than or equal to 0, and less than 2^24.'
)
iaas_subnet_create_201 = (
    'You do not have permission to make this request. Your Member must be self managed in order to create Subnet '
    'records.'
)

# Read
iaas_subnet_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Subnet record.'
iaas_subnet_read_201 = (
    'You do not have permission to make this request. Robots can only read Subnets in their region.'
)
iaas_subnet_read_202 = (
    'You do not have permission to make this request. As a global user, you will need to change to the Address that '
    'owns the Subnet to complete request.'
)
iaas_subnet_read_203 = (
    'You do not have permission to make this request. You can only read cloud Subnets that belong to your own Address.'
)

iaas_subnet_read_204 = (
    'You do not have permission to make this request. You can only read Subnets that are owned by your Address, reside '
    'in parent Subnets or Allocations owned by your Address, or are owned by an Address your Address is linked to.'
)
iaas_subnet_read_205 = (
    'You do not have permission to make this request. You can only read Subnets that are owned by linked Addresses in '
    'non self managed Members.'
)

# Update
iaas_subnet_update_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Subnet record.'
iaas_subnet_update_101 = 'The "address_id" parameter is invalid. "address_id" is required.'
iaas_subnet_update_102 = 'The "address_id" parameter is invalid. "address_id" must be a valid integer.'
iaas_subnet_update_103 = 'The "address_id" parameter is invalid. "address_id" for a cloud subnet cannot be modified.'
iaas_subnet_update_104 = (
    'The "address_id" parameter is invalid. "address_id" must be the ID of your Address or an Address you are linked '
    'to.'
)
iaas_subnet_update_105 = 'The "parent_id" parameter is invalid. "parent_id" is not allowed for a cloud subnet.'
iaas_subnet_update_106 = 'The "parent_id" parameter is invalid. "parent_id" must be a valid integer.'
iaas_subnet_update_107 = (
    'The "parent_id" parameter is invalid. "parent_id" does not correspond with a valid Subnet record.'
)
iaas_subnet_update_108 = (
    'The "parent_id" parameter is invalid. "parent_id" does not correspond with a Subnet record in the '
    'Allocation of the existing Subnet record.'
)
iaas_subnet_update_109 = (
    'The "parent_id" parameter is invalid. "parent_id" must correspond with a Subnet record owned by '
    'your Address or a linked Address.'
)
iaas_subnet_update_110 = 'The "address_range" parameter is invalid. "address_range" is required.'
iaas_subnet_update_111 = (
    'The "address_range" parameter is invalid. "address_range" must be a string containing a valid Subnet.'
)
iaas_subnet_update_112 = (
    'The "address_range" parameter is invalid. The chosen "address_range" does not contain all of the address ranges '
    'of the children of this Subnet record.'
)
iaas_subnet_update_113 = (
    'The "address_range" parameter is invalid. "address_range" does not use the same IP version as the address range '
    'of the Allocation of the Subnet.'
)
iaas_subnet_update_114 = (
    'The "address_range" parameter is invalid. "address_range" is not a subnet within the address range of the '
    'Allocation of the Subnet.'
)
iaas_subnet_update_115 = (
    'The "address_range" parameter is invalid. Another Subnet with the chosen "address_range" already exists in the '
    'Allocation for the Subnet.'
)
iaas_subnet_update_116 = (
    'The "address_range" parameter is invalid. "address_range" overlaps with another Subnet in the Allocation for '
    'this Subnet'
)
iaas_subnet_update_117 = (
    'The "address_range" parameter is invalid. "address_range" does not use the same IP version as the address range '
    'of the parent Subnet.'
)
iaas_subnet_update_118 = (
    'The "address_range" parameter is invalid. "address_range" is not a subnet within the address range of the '
    'parent Subnet.'
)
iaas_subnet_update_119 = 'The "name" parameter is invalid. "name" cannot be longer than 128 characters.'
iaas_subnet_update_120 = 'The "vlan" parameter is invalid. "vlan" must be a valid integer.'
iaas_subnet_update_121 = 'The "vlan" parameter is invalid. "vlan" for a cloud subnet cannot be modified.'
iaas_subnet_update_122 = (
    'The "vlan" parameter is invalid. "vlan" must be greater than or equal to 0, and less than 4095.'
)
iaas_subnet_update_123 = 'The "vxlan" parameter is invalid. "vxlan" must be a valid integer.'
iaas_subnet_update_124 = 'The "vxlan" parameter is invalid. "vxlan" for a cloud subnet cannot be modified.'
iaas_subnet_update_125 = (
    'The "vxlan" parameter is invalid. "vxlan" must be greater than or equal to 0, and less than 2^24.'
)
iaas_subnet_update_201 = (
    'You do not have permission to make this request. Your Member must be self managed in order to update Subnet '
    'records.'
)
iaas_subnet_update_202 = (
    'You do not have permission to make this request. Cloud Subnets can be updated by updating the Virtual Router they '
    'are configured on'
)
iaas_subnet_update_203 = (
    'You do not have permission to make this request. You can only update Subnets that are owned by your Address, '
    'reside in parent Subnets or Allocations owned by your Address, or are owned by an Address your Address is linked '
    'to.'
)
iaas_subnet_update_204 = (
    'You do not have permission to make this request. You can only update Subnets that are owned by linked Addresses '
    'in non self managed Members.'
)

# Delete
iaas_subnet_delete_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid Subnet record.'
iaas_subnet_delete_201 = (
    'You do not have permission to make this request. Your Member must be self managed in order to delete Subnet '
    'records.'
)
iaas_subnet_delete_202 = (
    'You do not have permission to make this request. The specified Subnet still has children Subnets. '
    'Please delete this first before attempting to delete this Subnet again.'
)
iaas_subnet_delete_203 = (
    'You do not have permission to make this request. Cloud Subnets can only be deleted by updating or deleting the '
    'Virtual Router it is configured on'
)
iaas_subnet_delete_204 = (
    'You do not have permission to make this request. You can only delete Subnets that are owned by your Address, '
    'reside in parent Subnets or Allocations owned by your Address, or are owned by an Address your Address is linked '
    'to.'
)
iaas_subnet_delete_205 = (
    'You do not have permission to make this request. You can only delete Subnets that are owned by linked Addresses '
    'in non self managed Members.'
)

# Subnet Space List
iaas_subnet_space_list_001 = (
    'The "allocation_id" path parameter is invalid. "allocation_id" does not correspond with a valid Allocation '
    'record.'
)
