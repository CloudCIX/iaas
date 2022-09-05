"""
Error Codes for all of the methods in the StorageType service
"""

# List
iaas_storage_type_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Read
iaas_storage_type_read_001 = (
    'The "pk" path parameter is invalid. "pk" does not correspond to a valid StorageType record.'
)

# Update
iaas_storage_type_update_001 = (
    'The "pk" path parameter is invalid. "pk" does not correspond to a valid StorageType record.'
)
iaas_storage_type_update_101 = 'The "regions" parameter is invalid. The "regions" parameter must be a list.'
iaas_storage_type_update_102 = 'The "regions" parameter is invalid. The "regions" cannot be an empty list.'
iaas_storage_type_update_103 = (
    'The "regions" parameter is invalid. The "regions" parameter must be a list containing valid integers.'
)
iaas_storage_type_update_104 = (
    'An error occurred while attempting to validate the "regions" parameter against our Membership API. Please try '
    'again later or contact CloudCIX Support if it persists.'
)
iaas_storage_type_update_105 = (
    'The "regions" parameter is invalid. "regions" must be a list of valid IDs for Addresses you are linked to. One or '
    'more of the IDs in "regions" does not correspond with a valid linked Address.'
)
iaas_storage_type_update_106 = (
    'The "regions" parameter is invalid. Only Addresses that are cloud_region can be used as a region for CloudCIX.'
)
iaas_storage_type_update_201 = (
    'You do not have permission to make this request. Only administrators in Address 1 can update a StorageType.'
)
