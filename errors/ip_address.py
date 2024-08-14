"""
Error Codes for the IP Address Service
"""
# List
iaas_ip_address_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_ip_address_create_101 = 'The "subnet_id" parameter is invalid. "subnet_id" is required'
iaas_ip_address_create_102 = 'The "subnet_id" parameter is invalid. "subnet_id" must be an integer.'

iaas_ip_address_create_103 = (
    'The "subnet_id" parameter is invalid. "subnet_id" does not correspond to a valid Subnet record.'
)
iaas_ip_address_create_104 = 'The "address" parameter is invalid. "address" is required.'
iaas_ip_address_create_105 = (
    'The "address" parameter is invalid. "address" is not a string containing a correctly formatted IP Address.'
)
iaas_ip_address_create_106 = (
    'The "address" parameter is invalid. "address" is not an address within the range of the chosen Subnet.'
)
iaas_ip_address_create_107 = (
    'The "address" parameter is invalid. There is another IPAddress record with the same "address" in the chosen '
    'Subnet.'
)
iaas_ip_address_create_108 = 'The "name" parameter is invalid. "name" cannot be longer than 64 characters.'
iaas_ip_address_create_109 = 'The "location" parameter is invalid. "location" cannot be longer than 64 characters.'
iaas_ip_address_create_110 = (
    'The "credentials" parameter is invalid. "credentials" cannot be longer than 64 characters.'
)
iaas_ip_address_create_201 = (
    'You do not have permission to create this IP Address. Your Address must own the specified Subnet record to '
    'create IPAddress records.'
)

# Read
iaas_ip_address_read_001 = 'The "pk" path parameter is invalid. "pk" must correspond to a valid IPAddress record.'
iaas_ip_address_read_002 = (
    'There was an issue with the IPAddress record. The requested IP Address is marked as a floating cloud IP but is '
    'associated with more than one private IP Address record. Please contact CloudCIX support.'
)
iaas_ip_address_read_201 = (
    'You do not have permission to read this Cloud IPAddress. Robot can only read IPs from networks in it\'s region.'
)
iaas_ip_address_read_202 = (
    'You do not have permission to read this Cloud IPAddress. Robot can only read IPs for project networks in it\'s '
    'regiom.'
)
iaas_ip_address_read_203 = (
    'You do not have permission to read this Cloud IPAddress. You can only read public IPs NATted to a VM in your '
    'address.'
)
iaas_ip_address_read_204 = (
    'You do not have permission to read this Cloud IPAddress. You can only read public IPs assigned to Virtual Routers '
    'for Projects in your address.'
)
iaas_ip_address_read_205 = (
    'You do not have permission to read this IPAddress. Your Address must own the IP Address Subnet record.'
)

# Update
iaas_ip_address_update_001 = 'The "ip" path parameter is invalid. "ip" must belong to a valid ip_address record.'
iaas_ip_address_update_002 = (
    'There was an issue with the IPAddress record. The IPAddress is marked as being for the cloud but its associated '
    'ASN was not associated with a Project. Are you attempting to delete the public IP for a NATted IP?'
)
iaas_ip_address_update_003 = (
    'There was an issue with the IPAddress record. The Project associated with the IPAddress record could not be '
    'accessed.'
)
iaas_ip_address_update_101 = (
    'The "address" parameter is invalid. "address" is not a string containing a correctly formatted IP Address.'
)
iaas_ip_address_update_102 = (
    'The "address" parameter is invalid. "address" is not an IP Address within the range of the chosen Subnet.'
)
iaas_ip_address_update_103 = (
    'The "address" parameter is invalid. There is another IPAddress record with the same "address" in the chosen '
    'Subnet.'
)
iaas_ip_address_update_104 = 'The "name" parameter is invalid. "name" cannot be longer than 64 characters.'
iaas_ip_address_update_105 = 'The "location" parameter is invalid. "location" cannot be longer than 64 characters.'
iaas_ip_address_update_106 = (
    'The "credentials" parameter is invalid. "credentials" cannot be longer than 64 characters.'
)
iaas_ip_address_update_201 = (
    'You do not have permission to update this IPAddress. RFC1918 Project IPs must be updated by updating the Cloud '
    'Resource it is configured on.'
)
iaas_ip_address_update_202 = (
    'You do not have permission to update this IPAddress. Your Address must own the IP Address Subnet record.'
)
iaas_ip_address_update_203 = (
    'You do not have permission to update this IPAddress. The IP is assigned to a Virtaul Router or a VM in your '
    'region.'
)
# Delete
iaas_ip_address_delete_001 = 'The "ip" path parameter is invalid. "ip" must belong to a valid ip_address record.'
iaas_ip_address_delete_201 = (
    'You do not have permission to delete this IPAddress. RFC1918 Project IPs must be deleted by updating or deleting '
    'the Cloud Resource it is configured on.'
)
iaas_ip_address_delete_202 = (
    'You do not have permission to delete this IPAddress. Your Address must own the specified Subnet record.'
)
iaas_ip_address_delete_203 = (
    'You do not have permission to delete this IPAddress. The IP is assigned to a Virtaul Router or a VM in your '
    'region.'
)
