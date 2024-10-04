# python
from typing import Optional
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
from rest_framework.request import QueryDict
# local
from iaas.models import (
    IPAddress,
    Subnet,
)


__all__ = [
    'IPAddressCreateController',
    'IPAddressListController',
]


class IPAddressListController(ControllerBase):
    """
    Validates IPAddress data used to list IP Addresses
    """
    class Meta(ControllerBase.Meta):
        allowed_ordering = (
            'address',
            'name',
            'created',
            'updated',
        )

        search_fields = {
            'address': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'ping': (),
            'public_ip_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'scan': (),
            'subnet_id': ('in', ),
            'subnet__address_id': ('in',),
            'subnet__allocation__asn__member_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'subnet__allocation__asn__number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'subnet__virtual_router_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'subnet__vlan': ('in',),
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class IPAddressCreateController(ControllerBase):
    """
    Validates IPAddress data used to create IP Addresses
    """
    # Bring down the typing for self.data since mypy doesn't have access to the ControllerBase
    data: QueryDict
    # Keep track of whether or not the requested address is private.
    is_private: bool = False
    # Keep track of the project ID for the private IP address.
    project_id: int = -1

    class Meta:
        model = IPAddress
        validation_order = (
            'subnet_id',
            'address',
            'name',
            'location',
            'credentials',
        )

    def validate_subnet_id(self, subnet_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Subnet record that the IPAddress will be a part of.
        type: integer
        """
        if subnet_id is None:
            return 'iaas_ip_address_create_101'

        try:
            subnet = Subnet.objects.get(pk=int(subnet_id))
        except (TypeError, ValueError):
            return 'iaas_ip_address_create_102'
        except Subnet.DoesNotExist:
            return 'iaas_ip_address_create_103'

        self.cleaned_data['subnet'] = subnet
        return None

    def validate_address(self, address: Optional[str]) -> Optional[str]:
        """
        description: The ip address for the IPAddress record.
        type: string
        """
        if 'subnet' not in self.cleaned_data:
            return None
        subnet: Subnet = self.cleaned_data['subnet']

        if address is None:
            return 'iaas_ip_address_create_104'

        try:
            ip_address = netaddr.IPAddress(address)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_ip_address_create_105'
        self.is_private = ip_address.is_global() is False

        network = netaddr.IPNetwork(subnet.address_range)
        if ip_address not in network:
            return 'iaas_ip_address_create_106'

        # Save the converted form of the IPAddress object as the string value for consistency.
        address = str(ip_address)

        if subnet.ip_addresses.filter(address=address).exists():
            return 'iaas_ip_address_create_107'

        self.cleaned_data['address'] = address
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name given to the IP Address.
        type: string
        required: false
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) > self.get_field('name').max_length:
            return 'iaas_ip_address_create_108'

        self.cleaned_data['name'] = name
        return None

    def validate_location(self, location: Optional[str]) -> Optional[str]:
        """
        description: |
            The location of the IPAddress.
            Can be used along with name to provide some reference information on the record.
        type: string
        required: false
        """
        if location is None:
            location = ''
        location = str(location).strip()
        if len(location) > self.get_field('location').max_length:
            return 'iaas_ip_address_create_109'

        self.cleaned_data['location'] = location
        return None

    def validate_credentials(self, credentials: Optional[str]) -> Optional[str]:
        """
        description: |
            The credentials for an IPAddress.
            Can be used to store username and password information along with an IP Address.
        type: string
        required: false
        """
        if credentials is None:
            credentials = ''
        credentials = str(credentials).strip()
        if len(credentials) > self.get_field('credentials').max_length:
            return 'iaas_ip_address_create_110'

        self.cleaned_data['credentials'] = credentials
        return None


class IPAddressUpdateController(ControllerBase):
    """
    Validates IPAddress data used to update IP Addresses
    """
    _instance: IPAddress

    class Meta:
        model = IPAddress
        validation_order = (
            'address',
            'name',
            'location',
            'credentials',
        )

    def validate_address(self, address: Optional[str]) -> Optional[str]:
        """
        description: the address is the ip address for this object
        type: string
        """
        if address is None:
            address = self._instance.address

        # Ensure the sent address is correctly formatted.
        try:
            ip_address = netaddr.IPAddress(address)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_ip_address_update_101'
        address = str(ip_address)

        if address == self._instance.address:
            # address not changed, no need to further validate
            return None

        # At this point we know the address has been changed
        # validate that IPAddress is in the network
        network = netaddr.IPNetwork(self._instance.subnet.address_range)
        if ip_address not in network:
            return 'iaas_ip_address_update_102'

        # validate that IPAddress does not overlap with other ip in the subnet
        if self._instance.subnet.ip_addresses.filter(address=address).exclude(pk=self._instance.pk).exists():
            return 'iaas_ip_address_update_103'

        self.cleaned_data['address'] = address
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name given to the IP Address.
        type: string
        required: false
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) > self.get_field('name').max_length:
            return 'iaas_ip_address_update_104'

        self.cleaned_data['name'] = name
        return None

    def validate_location(self, location: Optional[str]) -> Optional[str]:
        """
        description: |
            The location of the IPAddress.
            Can be used along with name to provide some reference information on the record.
        type: string
        required: false
        """
        if location is None:
            location = ''
        location = str(location).strip()
        if len(location) > self.get_field('location').max_length:
            return 'iaas_ip_address_update_105'

        self.cleaned_data['location'] = location
        return None

    def validate_credentials(self, credentials: Optional[str]) -> Optional[str]:
        """
        description: |
            The credentials for an IPAddress.
            Can be used to store username and password information along with an IP Address.
        type: string
        required: false
        """
        if credentials is None:
            credentials = ''
        credentials = str(credentials).strip()
        if len(credentials) > self.get_field('credentials').max_length:
            return 'iaas_ip_address_update_106'

        self.cleaned_data['credentials'] = credentials
        return None
