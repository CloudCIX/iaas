"""
Error Codes for all of the Methods in the Metrics Service
"""

# Read
iaas_metrics_read_001 = (
    'The "region_id" path parameter is invalid. The requested region has no hardware associated with it.'
)
iaas_metrics_read_101 = 'The "force" parameter is invalid. "force" must be a valid boolean.'
iaas_metrics_read_201 = (
    'You do not have permission to make this request. Metrics of a region can only be read by the PAM user.'
)
