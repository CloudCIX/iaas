# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import netaddr
# local
from iaas.models import AppSettings


__all__ = [
    'AppSettingsCreateController',
    'AppSettingsUpdateController',
]


class AppSettingsCreateController(ControllerBase):
    """
    Validates AppSettings data used to create a new AppSettings record
    """

    class Meta(ControllerBase.Meta):
        model = AppSettings
        validation_order = (
            'ipmi_host',
            'ipmi_credentials',
            'ipmi_username',
            'rage4_api_key',
            'rage4_email',
        )

    def validate_ipmi_host(self, ipmi_host: Optional[str]) -> Optional[str]:
        """
        description: The IP address for the IPMI host.
        required: false
        type: string
        """
        if ipmi_host is None:
            return None

        try:
            ip = netaddr.IPAddress(ipmi_host)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_app_settings_create_101'

        if ip.is_global() is False:
            return 'iaas_app_settings_create_102'

        self.cleaned_data['ipmi_host'] = str(ip)
        return None

    def validate_ipmi_credentials(self, ipmi_credentials: Optional[str]) -> Optional[str]:
        """
        description: The credential for the IPMI host.
        required: false
        type: string
        """
        if ipmi_credentials is None:
            return None

        ipmi_credentials = str(ipmi_credentials).strip()
        if len(ipmi_credentials) > self.get_field('ipmi_credentials').max_length:
            return 'iaas_app_settings_create_103'

        self.cleaned_data['ipmi_credentials'] = ipmi_credentials
        return None

    def validate_ipmi_username(self, ipmi_username: Optional[str]) -> Optional[str]:
        """
        description: The username for the IPMI host.
        required: false
        type: string
        """
        if ipmi_username is None:
            return None
        ipmi_username = str(ipmi_username).strip()
        if len(ipmi_username) > self.get_field('ipmi_username').max_length:
            return 'iaas_app_settings_create_104'

        self.cleaned_data['ipmi_username'] = ipmi_username
        return None

    def validate_rage4_api_key(self, rage4_api_key: Optional[str]) -> Optional[str]:
        """
        description: The API Key for Rage4 authentication to manage Public DNS records.
        required: false
        type: string
        """
        if rage4_api_key is None:
            return None

        self.cleaned_data['rage4_api_key'] = str(rage4_api_key).strip()
        return None

    def validate_rage4_email(self, rage4_email: Optional[str]) -> Optional[str]:
        """
        description: The email for Rage4 authentication to manage Public DNS records.
        required: false
        type: string
        """
        if rage4_email is None:
            return None
        rage4_email = str(rage4_email).strip()
        if len(rage4_email) > self.get_field('rage4_email').max_length:
            return 'iaas_app_settings_create_105'
        # Ensure it is a valid email
        try:
            validate_email(rage4_email)
        except ValidationError:
            return 'iaas_app_settings_create_106'
        self.cleaned_data['rage4_email'] = rage4_email.lower()
        return None


class AppSettingsUpdateController(ControllerBase):
    """
    Validates AppSettings data used to update an existing AppSettings
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = AppSettings
        validation_order = (
            'ipmi_host',
            'ipmi_credentials',
            'ipmi_username',
            'rage4_api_key',
            'rage4_email',
        )

    def validate_ipmi_host(self, ipmi_host: Optional[str]) -> Optional[str]:
        """
        description: The ip address for the IPMI host.
        required: false
        type: string
        """
        if ipmi_host is None:
            return None

        try:
            ip = netaddr.IPAddress(ipmi_host)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_app_settings_update_101'

        if ip.is_global() is False:
            return 'iaas_app_settings_update_102'

        self.cleaned_data['ipmi_host'] = str(ip)
        return None

    def validate_ipmi_credentials(self, ipmi_credentials: Optional[str]) -> Optional[str]:
        """
        description: The credential for the IPMI host.
        required: false
        type: string
        """
        if ipmi_credentials is None:
            return None

        ipmi_credentials = str(ipmi_credentials).strip()
        if len(ipmi_credentials) > self.get_field('ipmi_credentials').max_length:
            return 'iaas_app_settings_update_103'

        self.cleaned_data['ipmi_credentials'] = ipmi_credentials
        return None

    def validate_ipmi_username(self, ipmi_username: Optional[str]) -> Optional[str]:
        """
        description: The username for the IPMI host.
        required: false
        type: string
        """
        if ipmi_username is None:
            return None
        ipmi_username = str(ipmi_username).strip()
        if len(ipmi_username) > self.get_field('ipmi_username').max_length:
            return 'iaas_app_settings_update_104'

        self.cleaned_data['ipmi_username'] = ipmi_username
        return None

    def validate_rage4_api_key(self, rage4_api_key: Optional[str]) -> Optional[str]:
        """
        description: The API Key for Rage4 authentication to manage Public DNS records
        required: false
        type: string
        """
        if rage4_api_key is None:
            return None

        self.cleaned_data['rage4_api_key'] = str(rage4_api_key).strip()
        return None

    def validate_rage4_email(self, rage4_email: Optional[str]) -> Optional[str]:
        """
        description: The email for Rage4 authentication to manage Public DNS records
        required: false
        type: string
        """
        if rage4_email is None:
            return None
        rage4_email = str(rage4_email).strip()
        if len(rage4_email) > self.get_field('rage4_email').max_length:
            return 'iaas_app_settings_update_105'
        # Ensure it is a valid email
        try:
            validate_email(rage4_email)
        except ValidationError:
            return 'iaas_app_settings_update_106'
        self.cleaned_data['rage4_email'] = rage4_email.lower()
        return None
