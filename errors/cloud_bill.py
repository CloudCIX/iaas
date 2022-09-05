"""
Error Codes for all of the Methods in the Cloud Bill Service
"""

# List
iaas_cloud_bill_list_001 = (
    'The "timestamp" query parameter is invalid. "timestamp" must be a date time string in ISO 8601 format.'
)

# Read
iaas_cloud_bill_read_001 = (
    'The "project_id" path parameter is invalid. A Project with that id does not exist.'
)
iaas_cloud_bill_read_002 = (
    'The "timestamp" query parameter is invalid. "timestamp" must be a date time string in ISO 8601 format.'
)
iaas_cloud_bill_read_201 = (
    'You do not have permission to make this request.'
)
