# python
from collections import deque
from typing import Any, Deque, Dict, Optional
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
from cloudcix_rest.utils import get_error_details

__all__ = [
    'IPValidatorController',
]

NETWORK_CLASSES = {
    # IPv4
    4: {
        netaddr.IPNetwork('10.0.0.0/8'): {
            'reference': 'RFC 1918',
            'present_use': 'Private-Use Networks',
        },
        netaddr.IPNetwork('172.16.0.0/12'): {
            'reference': 'RFC 1918',
            'present_use': 'Private-Use Networks',
        },
        netaddr.IPNetwork('192.168.0.0/16'): {
            'reference': 'RFC 1918',
            'present_use': 'Private-Use Networks',
        },
        netaddr.IPNetwork('192.0.2.0/24'): {
            'reference': 'RFC 5737',
            'present_use': 'TEST-NET-1',
        },
        netaddr.IPNetwork('198.51.100.0/24'): {
            'reference': 'RFC 5737',
            'present_use': 'TEST-NET-2',
        },
        netaddr.IPNetwork('203.0.113.0/24'): {
            'reference': 'RFC 5737',
            'present_use': 'TEST-NET-3',
        },
        netaddr.IPNetwork('0.0.0.0/8'): {
            'reference': 'RFC 1122',
            'present_use': '"This" Network',
        },
        netaddr.IPNetwork('127.0.0.0/8'): {
            'reference': 'RFC 1122',
            'present_use': 'Loopback',
        },
        netaddr.IPNetwork('240.0.0.0/4'): {
            'reference': 'RFC 1122',
            'present_use': 'Reserved for Future Use',
        },
        netaddr.IPNetwork('169.254.0.0/16'): {
            'reference': 'RFC 3927',
            'present_use': 'Link Local',
        },
        netaddr.IPNetwork('192.0.0.0/24'): {
            'reference': 'RFC 5736',
            'present_use': 'IETF Protocol Assignments',
        },
        netaddr.IPNetwork('192.88.99.0/24'): {
            'reference': 'RFC 3068',
            'present_use': '6to4 Relay Anycast',
        },
        netaddr.IPNetwork('198.18.0.0/15'): {
            'reference': 'RFC 2544',
            'present_use': 'Network Interconnect Device Benchmark Testing',
        },
        netaddr.IPNetwork('224.0.0.0/4'): {
            'reference': 'RFC 3171',
            'present_use': 'Multicast',
        },
        netaddr.IPNetwork('255.255.255.255/32'): {
            'reference': 'RFC 919, RFC 922',
            'present_use': 'Limited Broadcast',
        },
        # Default
        netaddr.IPNetwork('0.0.0.0/0'): {
            'reference': 'IPv4',
            'present_use': 'Public-Use Networks',
        },
    },
    # IPv6
    6: {
        netaddr.IPNetwork('fd00::/7'): {
            'reference': 'RFC 4193',
            'present_use': 'Unique-local Network',
        },
        netaddr.IPNetwork('2001:20::/28'): {
            'reference': 'RFC 7343',
            'present_use': 'ORCHIDv2',
        },
        netaddr.IPNetwork('::ffff:0:0/96'): {
            'reference': 'RFC 4291',
            'present_use': 'IPv4-mapped Address',
        },
        netaddr.IPNetwork('2001::/23'): {
            'reference': 'RFC 2928',
            'present_use': 'IETF Protocol Assignments',
        },
        # Default
        netaddr.IPNetwork('::/0'): {
            'reference': 'IPv6',
            'present_use': 'Public-Use Networks',
        },
    },
}
MASK_ERRORS = {4: 'iaas_ip_validator_104', 6: 'iaas_ip_validator_105'}


class IPValidatorController(ControllerBase):
    """
    Validates ipaddresses and ranges
    """

    # Keep track of a list of address ranges that were sent
    address_ranges: Deque[netaddr.IPNetwork] = deque()

    class Meta(ControllerBase.Meta):
        validation_order = (
            'address_ranges',
            'ip_addresses',
            'errors',
        )

    def validate_address_ranges(self, address_ranges: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing one or more gateway addresses for address ranges in CIDR notation, separated by commas.
            These address ranges will be validated to ensure they are correct, and will be returned along with some
            extra information about them that helps define the type of network they represent.
        type: string
        """
        # Put an initial value into the address_ranges field
        self.cleaned_data['address_ranges'] = {}

        if address_ranges is None:
            address_ranges = ''
        if len(address_ranges) == 0:
            return None
        details: Dict[str, Dict[str, Any]] = {}

        # First, split the address_ranges by commas to get each of the individual ranges.
        ranges = address_ranges.split(',')

        # Iterate through each sent address range and validate them.
        for address_range in ranges:
            range_details: Dict[str, Any] = {
                'error': None,
                'valid': False,
                'details': None,
            }
            details[address_range] = range_details

            # Ensure that a properly formatted address range was sent.
            # This means an address and mask separated by a '/' character.
            range_split = address_range.split('/')
            if len(range_split) != 2:
                range_details['error'] = 'iaas_ip_validator_101'
                continue

            # Check the address part.
            address, mask = range_split
            try:
                ip_address = netaddr.IPAddress(address)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                range_details['error'] = 'iaas_ip_validator_102'
                continue

            # Check that the mask is a proper integer.
            try:
                int(mask)
            except (TypeError, ValueError):
                range_details['error'] = 'iaas_ip_validator_103'
                continue

            # Now, using `netaddr`, determine that the whole thing is a valid network.
            # If it isn't, it's all because of the mask value.
            try:
                network = netaddr.IPNetwork(address_range)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                range_details['error'] = MASK_ERRORS[ip_address.version]
                continue

            # Add the network to the deque of ranges for the ip_address validation
            self.address_ranges.append(network)

            # At this stage, the address range is valid.
            range_details['valid'] = True

            # Now go fetch the information to put in the 'details' key.
            info: Dict[str, Any] = {
                'ipv4': ip_address.version == 4,
                'ipv6': ip_address.version == 6,
                'network_address': str(network.network),
                'netmask_address': str(network.netmask),
                'hostmask_address': str(network.hostmask),
                'broadcast_address': str(network.broadcast),
                'cidr': str(network.cidr),
            }
            # Determine the values for reference and present_use for the range.
            for network_class, class_info in NETWORK_CLASSES[ip_address.version].items():
                if network in network_class:
                    info.update(class_info)
                    break

            # Save the generated info
            range_details['details'] = info

        # Save the cleaned_data
        self.cleaned_data['address_ranges'] = details
        return None

    def validate_ip_addresses(self, ip_addresses: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing one or more IP addresses, separated by commas.
            These addresses will be validated to ensure they are in the correct format, and will be returned along with
            some extra information about them that helps understand the type of address they represent.
            Also, if `address` ranges are also sent, then the addresses sent will also be double checked to ensure that
            they fit into one of the provided address ranges, and will be marked as such.
        type: string
        """
        # Put an initial value into the ip_addresses field
        self.cleaned_data['ip_addresses'] = {}

        if ip_addresses is None:
            ip_addresses = ''
        if len(ip_addresses) == 0:
            return None
        details: Dict[str, Dict[str, Any]] = {}

        # First, split the ip_addresses by commas to get each of the individual addresses.
        addresses = ip_addresses.split(',')

        # Iterate through each sent address and validate them.
        for address in addresses:
            address_details: Dict[str, Any] = {
                'error': None,
                'valid': False,
                'details': None,
            }
            details[address] = address_details

            # Check that the sent address is formatted correctly.
            try:
                ip_address = netaddr.IPAddress(address)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                address_details['error'] = 'iaas_ip_validator_106'
                continue

            # At this stage, the address is valid.
            address_details['valid'] = True

            # Now go fetch the information to put in the 'details' key.
            info: Dict[str, Any] = {
                'ipv4': ip_address.version == 4,
                'ipv6': ip_address.version == 6,
                'is_private': ip_address.is_global() is False,
                'is_reserved': ip_address.is_reserved(),
                'is_loopback': ip_address.is_loopback(),
                'parent_network': None,
            }

            # Find the sent address range that corresponds with this IP address
            for address_range in self.address_ranges:
                if ip_address in address_range:
                    info['parent_network'] = str(address_range)

            # Save the generated info
            address_details['details'] = info

        # Save the cleaned_data
        self.cleaned_data['ip_addresses'] = details
        return None

    def validate_errors(self, errors=None) -> Optional[str]:
        """
        description:
            Check for errors in the cleaned data and, if any are found, extend them out into their full forms
        generative: true
        """
        # First check the address_ranges
        missing: Deque[str] = deque()
        for details in self.cleaned_data.get('address_ranges', {}).values():
            if details['error'] is not None:
                error_code = details['error']
                try:
                    details['error'] = get_error_details(error_code)[error_code]
                except KeyError:  # pragma: no cover
                    missing.append(error_code)

        # Then do the ip_addresses
        for details in self.cleaned_data.get('ip_addresses', {}).values():
            if details['error'] is not None:
                error_code = details['error']
                try:
                    details['error'] = get_error_details(error_code)[error_code]
                except KeyError:  # pragma: no cover
                    missing.append(error_code)

        if len(missing) > 0:  # pragma: no cover
            raise KeyError(
                f'The following error codes were raised but no messages were defined for them; {", ".join(missing)}',
            )
        return None
