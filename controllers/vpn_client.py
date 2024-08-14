# stdlib
import re
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from jaeger_client import Span
from rest_framework.request import QueryDict, Request
# local
from iaas.models import VPNClient
from .junos_dollar_nine import encrypt

__all__ = [
    'VPNClientCreateController',
    'VPNClientUpdateController',
]

SPECIAL_CHAR_PATTERN_PASSWORD = re.compile(r'["\'@+\-\/\\|=]')
SPECIAL_CHAR_PATTERN_USERNAME = re.compile(r'["&()\\|?]')


class VPNClientCreateController(ControllerBase):
    """
    Validates user data used to create a new vpn Client record
    """

    class Meta(ControllerBase.Meta):
        model = VPNClient
        validation_order = (
            'password',
            'username',
        )

    def __init__(
            self,
            request: Request,
            data: QueryDict,
            span: Optional[Span],
            vpn_id: Optional[int],
    ) -> None:
        """
        Override the init to allow for adding extra fields from outside into the system.
        :param request: The request sent by the User
        :param data: The data being validated. Either request.GET or request.POST depending on the method
        :param span: A Span instance that is the parent span of the controller. Passing this in will allow us to record
                     time taken to run the validation methods in the controller.
        :param vpn_id: The ID of VPN the client is to be configured on. This is only required when adding a Client to an
                       existing VPN.
        """
        super(VPNClientCreateController, self).__init__(request=request, data=data, span=span)
        if vpn_id is not None:
            self.cleaned_data['vpn_id'] = vpn_id

    def validate_password(self, password: Optional[str]) -> Optional[str]:
        """
        description: |
            The password to use for setting up the VPN Clients of the Dynamic VPN Tunnel.

            Note that the password cannot contain any of the following special characters;
            - `"`
            - `'`
            - `@`
            - `+`
            - `-`
            - `/`
            - `\\`
            - `|`
            - `=`

            Also note that the default max length of the password is 255 characters.
        type: string
        """
        if password is None:
            return 'iaas_vpn_client_create_101'
        password = str(password)
        # Ensure the valid special chars
        if SPECIAL_CHAR_PATTERN_PASSWORD.search(password) is not None:
            return 'iaas_vpn_client_create_102'

        # check the length
        if len(password) > self.get_field('password').max_length:
            return 'iaas_vpn_client_create_103'

        # Encrypt the password, as CloudCIX policy that doesn't store plain text passwords in database.
        encrypted_password = encrypt(password)
        self.cleaned_data['password'] = encrypted_password
        return None

    def validate_username(self, username: Optional[str]) -> Optional[str]:
        """
        description: |
            The username to use for setting up the VPN Clients of the Dynamic VPN Tunnel.

            Note that the username cannot contain any of the following special characters;
            - `"`
            - `&`
            - `(`
            - `)`
            - `\\`
            - `|`
            - `?`

            Also note that the default max length of the username is 255 characters.
        type: string
        """
        # Ensure a value was sent
        if username is None:
            return 'iaas_vpn_client_create_104'
        username = str(username)
        # Ensure the valid special chars
        if SPECIAL_CHAR_PATTERN_USERNAME.search(username) is not None:
            return 'iaas_vpn_client_create_105'

        # check the length
        if len(username) > self.get_field('username').max_length:
            return 'iaas_vpn_client_create_106'

        self.cleaned_data['username'] = username
        return None


class VPNClientUpdateController(ControllerBase):
    """
    Validates user data used to update a existing VPN Client record
    """
    _instance: VPNClient

    class Meta(ControllerBase.Meta):
        model = VPNClient
        validation_order = (
            'password',
            'username',
        )

    def validate_password(self, password: Optional[str]) -> Optional[str]:
        """
        description: |
            The password to use for setting up the VPN Clients of the Dynamic VPN Tunnel.

            Note that the password cannot contain any of the following special characters;
            - `"`
            - `'`
            - `@`
            - `+`
            - `-`
            - `/`
            - `\\`
            - `|`
            - `=`

            Also note that the default max length of the password is 255 characters.
        type: string
        """
        if password is None or password.startswith('$9$'):
            return None

        # Ensure the valid special chars
        if SPECIAL_CHAR_PATTERN_PASSWORD.search(password) is not None:
            return 'iaas_vpn_client_update_101'

        # check the length
        if len(password) > self.get_field('password').max_length:
            return 'iaas_vpn_client_update_102'

        # Encrypt the password, as CloudCIX policy that doesn't store plain text passwords in database.
        encrypted_password = encrypt(password)

        self.cleaned_data['password'] = encrypted_password
        return None

    def validate_username(self, username: Optional[str]) -> Optional[str]:
        """
        description: |
            The username to use for setting up the VPN Clients of the Dynamic VPN Tunnel.

            Note that the username cannot contain any of the following special characters;
            - `"`
            - `&`
            - `(`
            - `)`
            - `\\`
            - `|`
            - `?`

            Also note that the default max length of the username is 255 characters.
        type: string
        """
        # Ensure a value was sent
        if username is None:
            username = self._instance.username
        username = str(username)
        # Ensure the valid special chars
        if SPECIAL_CHAR_PATTERN_USERNAME.search(username) is not None:
            return 'iaas_vpn_client_update_103'

        # check the length
        if len(username) > self.get_field('username').max_length:
            return 'iaas_vpn_client_update_104'

        self.cleaned_data['username'] = username
        return None
