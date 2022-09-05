# stdlib
import re
from typing import Optional
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Interface, Server

__all__ = [
    'InterfaceListController',
    'InterfaceCreateController',
    'InterfaceUpdateController',
]

MAC_ADDRESS_REGEX = re.compile('^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$')


class InterfaceListController(ControllerBase):
    """
    Lists the interfaces of a Server.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase meta to make it more specific
        to the InterfaceList.
        """
        allowed_ordering = (
            'created',
            'hostname',
            'ip_address',
            'mac_address',
            'server_id',
        )
        search_fields = {
            'details': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'enabled': (),
            'hostname': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'ip_address': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'mac_address': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'server_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class InterfaceCreateController(ControllerBase):
    """
    Validates interface data used to create an interface.
    """

    class Meta(ControllerBase.Meta):
        """
        Assign the model and validation order for fields.
        """
        model = Interface
        validation_order = (
            'server_id',
            'mac_address',
            'ip_address',
            'hostname',
            'details',
            'enabled',
        )

    def validate_server_id(self, server_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Server that the new Interface record will be associated with.
        type: integer
        """
        # Check if value is empty.
        if server_id is None:
            return 'iaas_interface_create_101'

        # Check if value is valid type.
        try:
            server_id = int(server_id)
        except (ValueError, TypeError):
            return 'iaas_interface_create_102'

        # Ensure it corresponds to a valid Server.
        try:
            server = Server.objects.get(pk=server_id)
        except Server.DoesNotExist:
            return 'iaas_interface_create_103'

        # If User isn't global ensure the Server is in their region.
        if not self.request.user.is_global and server.region_id != self.request.user.address['id']:
            return 'iaas_interface_create_104'

        self.cleaned_data['server'] = server
        return None

    def validate_mac_address(self, mac_address: Optional[str]) -> Optional[str]:
        """
        description: The MAC Address of the Interface.
        type: string
        """
        # Check if value is empty.
        if mac_address is None:
            return 'iaas_interface_create_105'

        # Clean value and check if valid format.
        mac_address = str(mac_address).strip().upper().replace('-', ':')
        if MAC_ADDRESS_REGEX.match(mac_address) is None:
            return 'iaas_interface_create_106'

        self.cleaned_data['mac_address'] = mac_address
        return None

    def validate_ip_address(self, ip_address: Optional[str]) -> Optional[str]:
        """
        description: The IP Address of the Interface. Optional.
        type: string
        required: false
        """
        # Value is optional
        if ip_address is None:
            return None

        # Check if IP address is valid IP address
        try:
            address = netaddr.IPAddress(ip_address)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_interface_create_107'

        self.cleaned_data['ip_address'] = str(address)
        return None

    def validate_hostname(self, hostname: Optional[str]) -> Optional[str]:
        """
        description: The optional hostname that corresponds with the IP Address of the Interface.
        type: string
        required: false
        """
        # Value is optional.
        if hostname is None:
            hostname = ''

        # Ensure value does not exceed field length.
        if len(hostname) > self.get_field('hostname').max_length:
            return 'iaas_interface_create_108'

        self.cleaned_data['hostname'] = hostname
        return None

    def validate_details(self, details: Optional[str]) -> Optional[str]:
        """
        description: Extra textual details about the Interface, for example the name of the Interface on the Server.
        type: string
        required: false
        """
        # Value is optional.
        if details is None:
            details = ''

        # Ensure value does not exceed field length.
        if len(details) > self.get_field('details').max_length:
            return 'iaas_interface_create_109'

        self.cleaned_data['details'] = details
        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: A flag that states whether or not the Interface is currently in use. Default is False.
        type: boolean
        required: false
        """
        if enabled is None:
            enabled = False

        # Ensure the value is of the correct type.
        if enabled not in {True, False}:
            return 'iaas_interface_create_110'

        self.cleaned_data['enabled'] = enabled
        return None


class InterfaceUpdateController(ControllerBase):
    """
    Validates interface data used to update an interface.
    """

    class Meta(ControllerBase.Meta):
        """
        Assign the model and validation order for fields.
        """

        model = Interface
        validation_order = (
            'details',
            'enabled',
            'hostname',
            'ip_address',
            'mac_address',
        )

    def validate_details(self, details: Optional[str]) -> Optional[str]:
        """
        description: Extra textual details about the Interface, for example the name of the Interface on the Server.
        type: string
        required: false
        """
        # Value is optional.
        if details is None:
            details = ''

        # Ensure value does not exceed field length.
        if len(details) > self.get_field('details').max_length:
            return 'iaas_interface_update_101'

        self.cleaned_data['details'] = details

        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: A flag that states whether or not the Interface is currently in use. Default is False.
        type: boolean
        required: false
        """
        # Value is optional.
        if enabled is None:
            enabled = False

        # Ensure the value is of the correct type.
        if enabled not in {True, False}:
            return 'iaas_interface_update_102'

        self.cleaned_data['enabled'] = enabled
        return None

    def validate_hostname(self, hostname: Optional[str]) -> Optional[str]:
        """
        description: The optional hostname that corresponds with the IP Address of the Interface.
        type: string
        required: false
        """
        # Value is optional.
        if hostname is None or hostname == self._instance.hostname:
            return None

        # Ensure value does not exceed field length.
        if len(hostname) > self.get_field('hostname').max_length:
            return 'iaas_interface_update_103'

        self.cleaned_data['hostname'] = hostname
        return None

    def validate_ip_address(self, ip_address: Optional[str]) -> Optional[str]:
        """
        description: The IP Address of the Interface. Optional.
        type: string
        required: false
        """
        # Value is optional
        if ip_address is None or ip_address == self._instance.ip_address:
            return None

        # Check if IP address is valid IP address
        try:
            address = netaddr.IPAddress(ip_address)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_interface_update_104'

        self.cleaned_data['ip_address'] = str(address)
        return None

    def validate_mac_address(self, mac_address: Optional[str]) -> Optional[str]:
        """
        description: The MAC Address of the Interface.
        type: string
        """
        # Check if value is empty.
        if mac_address is None or mac_address == self._instance.mac_address:
            return None

        # Clean value and check if valid format.
        mac_address = str(mac_address).strip().upper().replace('-', ':')
        if MAC_ADDRESS_REGEX.match(mac_address) is None:
            return 'iaas_interface_update_105'

        self.cleaned_data['mac_address'] = mac_address
        return None
