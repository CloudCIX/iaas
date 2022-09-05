"""
Error codes for the IPValidator service
"""

iaas_ip_validator_001 = (
    'This service requires either one or both of the "address_ranges" and "ip_addresses" parameters to be sent.'
)
iaas_ip_validator_101 = (
    'This address_range was sent in an invalid format. The address_range should be in the format '
    '(network_address)/(mask)'
)
iaas_ip_validator_102 = (
    'This address_range is invalid. The "network_address" portion of the address_range is not a valid IP address.'
)
iaas_ip_validator_103 = 'This address_range is invalid. The "mask" portion is not a valid integer.'
iaas_ip_validator_104 = (
    'This address_range is invalid. The "mask" portion must be between 0 and 32 for IPv4 address ranges.'
)
iaas_ip_validator_105 = (
    'This address_range is invalid. The "mask" portion must be between 0 and 128 for IPv6 address ranges.'
)
iaas_ip_validator_106 = 'This ip_address is invalid. The ip_address is not in a valid IP address format.'
