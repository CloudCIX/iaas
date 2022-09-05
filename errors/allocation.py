"""
Error Codes for all of the Methods in the Allocation Service
"""

# List
iaas_allocation_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_allocation_create_101 = (
    'The "address_id" parameter is invalid. "address_id" must be the ID of an Address that you are linked to, or your '
    'own Address.'
)
iaas_allocation_create_102 = 'The "asn_id" parameter is invalid. "asn_id" is required and must be an integer.'
iaas_allocation_create_103 = (
    'The "asn_id" parameter is invalid. "asn_id" must belong to a valid ASN record belonging to your Member'
)
iaas_allocation_create_104 = (
    'The "address_range" parameter is invalid. "address_range" is required and must be a valid address range in CIDR '
    'notation.'
)
iaas_allocation_create_105 = (
    'The "address_range" parameter is invalid. "address_range" overlaps with the address range of an existing '
    'Allocation record within the chosen ASN.'
)
iaas_allocation_create_106 = 'The "name" parameter is invalid. "name" is required and must be a string.'
iaas_allocation_create_107 = 'The "name" parameter is invalid. "name" cannot be longer than 64 characters.'
iaas_allocation_create_201 = 'You do not have permission to make this request. You must be an administrator.'
iaas_allocation_create_202 = 'You do not have permission to make this request. You must be from a self-managed Member.'

# Read
iaas_allocation_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Allocation record.'
iaas_allocation_read_201 = (
    'You do not have permission to make this request. You can only read Allocation records that are owned by your '
    'Address, or that are in an ASN owned by your Member.'
)

# Update
iaas_allocation_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Allocation record.'
iaas_allocation_update_101 = (
    'The "address_id" parameter is invalid. "address_id" must be the ID of an Address that you are linked to, or your '
    'own Address.'
)
iaas_allocation_update_102 = 'The "asn_id" parameter is invalid. "asn_id" is required and must be an integer.'
iaas_allocation_update_103 = (
    'The "asn_id" parameter is invalid. "asn_id" must belong to a valid ASN record belonging to your Member'
)
iaas_allocation_update_104 = (
    'The "address_range" parameter is invalid. "address_range" is required and must be a valid address range in CIDR '
    'notation.'
)
iaas_allocation_update_105 = (
    'The "address_range" parameter is invalid. "address_range" overlaps with the address range of another '
    'Allocation record within the chosen ASN.'
)
iaas_allocation_update_106 = 'The "name" parameter is invalid. "name" is required and must be a string.'
iaas_allocation_update_107 = 'The "name" parameter is invalid. "name" cannot be longer than 64 characters.'
iaas_allocation_update_201 = 'You do not have permission to make this request. You must be an administrator.'
iaas_allocation_update_202 = 'You do not have permission to make this request. You must be from a self-managed Member.'
iaas_allocation_update_203 = (
    'You do not have permission to make this request. You must own the ASN the Allocation belongs to in order to '
    'update its details.'
)

# Delete
iaas_allocation_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Allocation record.'
iaas_allocation_delete_201 = 'You do not have permission to make this request. You must be an administrator.'
iaas_allocation_delete_202 = 'You do not have permission to make this request. You must be from a self-managed Member.'
iaas_allocation_delete_203 = (
    'You do not have permission to make this request. You must own the ASN the Allocation belongs to in order to '
    'delete it.'
)
