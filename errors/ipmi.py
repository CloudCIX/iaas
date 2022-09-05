"""
Error Codes for all of the Methods in the IPMI Service
"""

# List
iaas_ipmi_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_ipmi_create_001 = (
    'An error occurred when attempting to create the IPMI record. The selected IPMI address is already in use for '
    'another public address, according to the router.'
)
iaas_ipmi_create_002 = (
    'An error occurred when attempting to create the IPMI record. An unexpected error occurred when attempting to '
    'delete the previous address book rules for the PoolIP record. Please contact CloudCIX.'
)
iaas_ipmi_create_003 = (
    'An error occurred when attempting to create the IPMI record. An unexpected error occurred when attempting to load '
    'the new config onto the router. Please contact CloudCIX.'
)
iaas_ipmi_create_004 = (
    'An error occurred when attempting to create the IPMI record. An error occurred when attempting to commit the '
    'changes to the router. Please contact CloudCIX.'
)
iaas_ipmi_create_005 = (
    'An error occurred when attempting to create the IPMI record. The API was unable to connect to the router to '
    'deploy any changes. Please contact CloudCIX.'
)
iaas_ipmi_create_006 = (
    'An error occurred when attempting to create the IPMI record. An unexpected error occurred during the process of '
    'interacting with the router.'
)
iaas_ipmi_create_101 = (
    'The "client_ip" parameter is invalid. "client_ip" is required and must be a string containing a valid IP address.'
)
iaas_ipmi_create_102 = 'The "customer_ip_id" parameter is invalid. "customer_ip_id" is required.'
iaas_ipmi_create_103 = 'The "customer_ip_id" parameter is invalid. "customer_ip_id" must be a valid integer.'
iaas_ipmi_create_104 = (
    'The "customer_ip_id" parameter is invalid. "customer_ip_id" does not correspond with a valid IPAddress record.'
)
iaas_ipmi_create_105 = (
    'The "customer_ip_id" parameter is invalid. "customer_ip_id" does not correspond with an IPAddress record in our '
    'OOB network.'
)
iaas_ipmi_create_201 = (
    'You do not have permission to make this request. Only Users in Member 1 can create new IPMI records.'
)

# Read
iaas_ipmi_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid IPMI record.'
iaas_ipmi_read_201 = (
    'You do not have permission to make this request. You can only read IPMI records that involve IPAddresses that '
    'your Address owns.'
)

# Delete
iaas_ipmi_delete_001 = 'The "pk" path parameter is invalid. "pk" does not correspond with a valid IPMI record.'
iaas_ipmi_delete_002 = (
    'An error occurred when attempting to delete the IPMI record. An unexpected error occurred when attempting to load '
    'the config onto the router. Please contact CloudCIX.'
)
iaas_ipmi_delete_003 = (
    'An error occurred when attempting to delete the IPMI record. An error occurred when attempting to commit the '
    'changes to the router. Please contact CloudCIX.'
)
iaas_ipmi_delete_004 = (
    'An error occurred when attempting to delete the IPMI record. The API was unable to connect to the router to '
    'deploy any changes. Please contact CloudCIX.'
)
iaas_ipmi_delete_005 = (
    'An error occurred when attempting to delete the IPMI record. An unexpected error occurred during the process of '
    'interacting with the router. Please contact CloudCIX.'
)
iaas_ipmi_delete_201 = (
    'You do not have permission to make this request. You can only delete IPMI records that involve IPAddresses that '
    'your Address owns.'
)

# get juniper devices
iaas_ipmi_get_juniper_device_001 = 'Access to the IPMI host to create an IPMI is not configured.'
