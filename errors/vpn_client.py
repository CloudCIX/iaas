"""
Error Codes for all of the Methods in the VPN Client Service
"""
# Create
iaas_vpn_client_create_101 = 'The "password" parameter is invalid. "password" is required.'
iaas_vpn_client_create_102 = (
    'The "password" parameter is invalid. `password` cannot contain any of \", \', @, +, -, /, \\, | and ='
    ' these special characters.'
)
iaas_vpn_client_create_103 = (
    'The "password" parameter is invalid. The password cannot be longer than 255 characters.'
)
iaas_vpn_client_create_104 = 'The "username" parameter is invalid. "username" is required.'

iaas_vpn_client_create_105 = (
    'The "username" parameter is invalid. `username` cannot contain any of (, ), &, \", | and ?'
    'these special characters.'
)
iaas_vpn_client_create_106 = (
    'The "username" parameter is invalid. The password cannot be longer than 255 characters.'
)
# Update
iaas_vpn_client_update_101 = (
    'The "password" parameter is invalid. `password` cannot contain any of \", \', @, +, -, /, \\, | and ='
    'these special characters'
)
iaas_vpn_client_update_102 = (
    'The "password" parameter is invalid. The password cannot be longer than 255 characters.'
)
iaas_vpn_client_update_103 = (
    'The "username" parameter is invalid. `username` cannot contain any of (, ), &, \", | and ?'
    ' these special characters.'
)
iaas_vpn_client_update_104 = (
    'The "username" parameter is invalid. The password cannot be longer than 255 characters.'
)
