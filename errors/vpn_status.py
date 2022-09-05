"""
Errors for VPN status view
"""

iaas_vpn_status_read_001 = (
    'The "vpn_id" path parameter is invalid. "vpn_id" must correspond with a valid VPN record.'
)
iaas_vpn_status_read_002 = 'Access to the Router to retrieve VPN status is not configured.'
iaas_vpn_status_read_003 = (
    'A valid management subnet could not be retrieved. Please try again later or contact CloudCIX support if this '
    'persists.'
)
iaas_vpn_status_read_004 = (
    'We could not connect to the Router to retrieve VPN status. Please try again later or contact CloudCIX support '
    'if this persists.'
)
iaas_vpn_status_read_201 = (
    'You do not have permission to execute this method. You do not own the Project record.'
)
