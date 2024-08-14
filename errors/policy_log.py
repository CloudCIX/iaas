"""
Errors for PolicyLog view
"""

iaas_policy_log_list_001 = (
    'The "project_id" path parameter is invalid. "project_id" must correspond with a valid Project record.'
)
iaas_policy_log_list_002 = 'Access to the Router to retrieve logs is not configured.'
iaas_policy_log_list_003 = (
    'A /48 IPv6 Region Assignemnt could not be retrieved. Please try again later or contact CloudCIX support if this '
    'persists.'
)
iaas_policy_log_list_004 = (
    'We could not connect to the Router to retrieve logs. Please try again later or contact CloudCIX support if this '
    'persists.'
)
iaas_policy_log_list_201 = (
    'You do not have permission to execute this method. You do not own the Project record.'
)
