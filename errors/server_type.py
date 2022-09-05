"""
Error Codes for all of the methods in the ServerType service
"""

# List
iaas_server_type_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Read
iaas_server_type_read_001 = 'The "pk" path parameter is invalid. "pk" does not correspond to a valid ServerType record.'
