"""
Error Codes for all of the Methods in the ASN Service
"""

# List
iaas_asn_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns, i.e. sending non-integer values for integer fields.'
)

# Create
iaas_asn_create_101 = (
    'The "member_id" parameter is invalid. "member_id" must be a valid ID for a Member you are linked to, or your own '
    'Member'
)
iaas_asn_create_102 = 'The "number" parameter is invalid. "number" is required and must be an integer.'
iaas_asn_create_103 = 'The "number" parameter is invalid. "number" must be within the allowed IANA range of 1 - 2^32.'
iaas_asn_create_104 = 'The "number" parameter is invalid. There is already an ASN with this number.'
iaas_asn_create_201 = (
    'You do not have permission to make this request. Only Users who are in Address 1 have permission to create '
    'non-cloud ASNs.'
)
iaas_asn_create_202 = (
    'You do not have permission to make this request. To create a Cloud ASN please request create Project'
)

# Read
iaas_asn_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid ASN record.'

# Update
iaas_asn_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid ASN record.'
iaas_asn_update_101 = (
    'The "member_id" parameter is invalid. "member_id" must be a valid ID for a Member you are linked to, or your own '
    'Member'
)
iaas_asn_update_102 = 'The "number" parameter is invalid. "number" is required and must be an integer.'
iaas_asn_update_103 = 'The "number" parameter is invalid. "number" must be within the allowed IANA range of 1 - 2^32.'
iaas_asn_update_104 = 'The "number" parameter is invalid. There is already an ASN with this number.'
iaas_asn_update_201 = (
    'You do not have permission to make this request. Only Users who are in Address 1 have permission to make requests '
    'to this service.'
)
iaas_asn_update_202 = (
    'You do not have permission to make this request. Only Users who are in Address 1 have permission to update '
    'non-cloud ASNs.'
)

# Delete
iaas_asn_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid ASN record.'
iaas_asn_delete_201 = (
    'You do not have permission to make this request. To delete a Cloud ASN please request delete Project'
)
iaas_asn_delete_202 = (
    'You do not have permission to make this request. Only Users who are in Address 1 have permission to delete '
    'non-cloud ASNs.'
)
