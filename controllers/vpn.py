# stdlib
from collections import deque
from datetime import datetime
import re
from typing import Any, Deque, Dict, List, Optional, cast
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import (
    Route,
    VirtualRouter,
    VPN,
    VPNClient,
)
from .route import RouteCreateController, RouteUpdateController
from .vpn_client import VPNClientCreateController, VPNClientUpdateController

__all__ = [
    'VPNCreateController',
    'VPNListController',
    'VPNUpdateController',
]

#  Define pattern of DNS label
#  Can begin and end with a number or letter only
#  Can contain hyphens, a-z, A-Z, 0-9
#  1 - 63 chars allowed
FQDN_PATTERN = re.compile(r'^[a-z0-9]([a-z-0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
SPECIAL_CHAR_PATTERN = re.compile(r'["\'@+\-\/\\|=]')
IKE_VERSION_CHOICES = dict(VPN.VERSIONS)
IPSEC_ESTABLISH_CHOICES = dict(VPN.ESTABLISH_TIMES)
TYPE_CHOICES = dict(VPN.TYPES)


class VPNListController(ControllerBase):
    """
    Validates User data used to filter a list of VPNs
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'id',
            'created',
            'updated',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'virtual_router_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'virtual_router__project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'virtual_router__project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'virtual_router__project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class VPNCreateController(ControllerBase):
    """
    Validates User data used to create a VPN Tunnel
    """
    subnet: Optional[netaddr.IPNetwork] = None

    class Meta(ControllerBase.Meta):
        """
        Override ControllerBase.Meta fields
        """
        model = VPN
        validation_order = (
            'virtual_router_id',
            'vpn_type',
            'description',
            'dns',
            'ike_authentication',
            'ike_dh_groups',
            'ike_gateway_type',
            'ike_gateway_value',
            'ike_encryption',
            'ike_lifetime',
            'ike_pre_shared_key',
            'ike_version',
            'ipsec_authentication',
            'ipsec_encryption',
            'ipsec_establish_time',
            'ipsec_pfs_groups',
            'ipsec_lifetime',
            'routes',
            'traffic_selector',
            'vpn_clients',
        )

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        Extra handling of the errors property for handling the routes/vpn_clients errors in the case its a list
        """
        routes_popped = False
        clients_popped = False
        routes_errors = self._errors.get('routes', None)
        clients_errors = self._errors.get('vpn_clients', None)
        if isinstance(routes_errors, list):
            # Remove it, call super and add it back in
            routes_errors = self._errors.pop('routes')
            routes_popped = True
        if isinstance(clients_errors, list):
            # Remove it, call super and add it back in
            clients_errors = self._errors.pop('vpn_clients')
            clients_popped = True
        errors = super(VPNCreateController, self).errors
        if routes_popped:
            errors['routes'] = routes_errors
        if clients_popped:
            errors['vpn_clients'] = clients_errors
        return errors

    def validate_virtual_router_id(self, virtual_router_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the VirtualRouter record that the new VPN Tunnel should be built in.
        type: integer
        """
        if virtual_router_id is None:
            return 'iaas_vpn_create_101'

        try:
            virtual_router_id = int(virtual_router_id)
        except (TypeError, ValueError):
            return 'iaas_vpn_create_102'

        try:
            virtual_router = VirtualRouter.objects.get(pk=virtual_router_id)
        except VirtualRouter.DoesNotExist:
            return 'iaas_vpn_create_103'

        if virtual_router.project.address_id != self.request.user.address['id']:
            return 'iaas_vpn_create_104'

        self.cleaned_data['virtual_router'] = virtual_router
        return None

    def validate_vpn_type(self, vpn_type: Optional[str]) -> Optional[str]:
        """
        description: |
            String value of the chosen type of VPN.

            The VPN types supported by CloudCIX are;
            - `site-to-site`
            - `dynamic-secure-connect`

            Please ensure the sent string matches one of these exactly.
        type: string
        """
        if vpn_type is None:
            vpn_type = ''
        vpn_type = str(vpn_type).strip()

        if vpn_type not in TYPE_CHOICES:
            return 'iaas_vpn_create_134'

        self.cleaned_data['vpn_type'] = vpn_type
        return None

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: An optional description of what the vpn is for.
        type: string
        required: false
        """
        if description is None:
            description = ''
        description = str(description).strip()
        self.cleaned_data['description'] = description
        return None

    def validate_dns(self, dns: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP Address of the Customer's DNS.
            Must be IPv4 for now.
            Required only for Dynamic Secure connect type VPNs.
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            if dns is None:
                dns = ''
            dns = str(dns).strip()
            if len(dns) == 0:
                return 'iaas_vpn_create_135'

            try:
                ip = netaddr.IPAddress(dns)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_vpn_create_136'

            # For now, check that it is IPv4
            if ip.version != 4:
                return 'iaas_vpn_create_137'

            self.cleaned_data['dns'] = str(ip)
        return None

    def validate_ike_authentication(self, authentication: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of authentication algorithms for the IKE phase of the
            VPN Tunnel.

            The IKE phase authentication algorithms supported by CloudCIX are;
            - `sha1`
            - `sha-256`
            - `sha-384`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `sha-256` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if authentication is None:
                authentication = ''
            authentication = str(authentication).strip()

            if len(authentication) == 0:
                return 'iaas_vpn_create_105'
            auth_algs = set(alg.strip() for alg in authentication.split(','))
            for alg in auth_algs:
                if alg not in VPN.IKE_AUTHENTICATION_ALGORITHMS:
                    return 'iaas_vpn_create_106'

            self.cleaned_data['ike_authentication'] = ','.join(auth_algs)
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ike_authentication'] = VPN.SHA256
        return None

    def validate_ike_dh_groups(self, dh_groups: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of Diffie-Helmen groups for the IKE phase of the VPN Tunnel.

            The IKE phase Diffie-Helmen groups supported by CloudCIX are;
            - `group1`
            - `group2`
            - `group5`
            - `group19`
            - `group20`
            - `group24`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `group19` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if dh_groups is None:
                dh_groups = ''
            dh_groups = str(dh_groups).strip()
            if len(dh_groups) == 0:
                return 'iaas_vpn_create_107'

            groups = set(group.strip() for group in dh_groups.split(','))
            for group in groups:
                if group not in VPN.DH_GROUPS:
                    return 'iaas_vpn_create_108'

            self.cleaned_data['ike_dh_groups'] = ','.join(groups)
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ike_dh_groups'] = VPN.DH_GROUP_19
        return None

    def validate_ike_gateway_type(self, ike_gateway_type: Optional[str]) -> Optional[str]:
        """
        description: |
            The type of data that is stored in the `ike_gateway_value` field.
            Can only be either "public_ip" or "hostname".
            Defaults to "public_ip".
        type: string
        """
        if ike_gateway_type is None:
            ike_gateway_type = 'public_ip'

        ike_gateway_type = str(ike_gateway_type).strip()

        if ike_gateway_type not in (VPN.GATEWAY_PUBLIC_IP, VPN.GATEWAY_HOSTNAME):
            return 'iaas_vpn_create_140'

        self.cleaned_data['ike_gateway_type'] = ike_gateway_type
        return None

    def validate_ike_gateway_value(self, ike_gateway_value: Optional[str]) -> Optional[str]:
        """
        description: |
            The value used as the IKE gateway for the VPN Tunnel.
            The type for this value depends on what type was set for the "ike_gateway_type" parameter.

            For "public_ip", this value must be a string containing an IPv4 address.
            For "hostname", this value must be a valid hostname.
        type: string
        """
        if 'ike_gateway_type' not in self.cleaned_data:
            # Can't do anything without this valid parameter
            return None

        if ike_gateway_value is None:
            ike_gateway_value = ''
        ike_gateway_value = str(ike_gateway_value).strip()

        if len(ike_gateway_value) == 0:
            return 'iaas_vpn_create_141'

        # Run different functions based on the type
        if self.cleaned_data['ike_gateway_type'] == VPN.GATEWAY_PUBLIC_IP:
            return self._validate_ike_gateway_ip(ike_gateway_value)
        else:
            return self._validate_ike_gateway_fqdn(ike_gateway_value)

    def _validate_ike_gateway_ip(self, ike_gateway_value: str) -> Optional[str]:
        """
        Ensure the value is a valid IP. stolen from the old public ip validation
        """
        if 'vpn_type' not in self.cleaned_data:
            return None

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            # We don't need this value for DSC VPNs so just ignore it
            self.cleaned_data['ike_gateway_value'] = '0.0.0.0'
            return None

        # Otherwise, we validate it properly
        try:
            ip = netaddr.IPAddress(ike_gateway_value)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_vpn_create_120'

        # For now, check that it is IPv4
        if ip.version != 4:
            return 'iaas_vpn_create_121'

        self.cleaned_data['ike_gateway_value'] = str(ip)
        return None

    def _validate_ike_gateway_fqdn(self, ike_gateway_value: str) -> Optional[str]:
        """
        Ensure the value is a valid FQDN.
        """
        if len(ike_gateway_value) >= 253:
            return 'iaas_vpn_create_142'

        # Remove trailing dot
        if ike_gateway_value[-1] == '.':
            ike_gateway_value = ike_gateway_value[0:-1]

        #  Split ike_gateway_value into list of DNS labels
        labels = ike_gateway_value.split('.')

        # Check for existence of at least one '.' and all labels match that pattern.
        if len(labels) > 1 and all(FQDN_PATTERN.match(label) for label in labels):
            self.cleaned_data['ike_gateway_value'] = ike_gateway_value
            return None
        return 'iaas_vpn_create_142'

    def validate_ike_encryption(self, encryption: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of encryption algorithms for the IKE phase of the VPN Tunnel.

            The IKE phase encryption algorithms supported by CloudCIX are;
            - `aes-128-cbc`
            - `aes-192-cbc`
            - `aes-256-cbc`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `aes-256-cbc` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if encryption is None:
                encryption = ''
            encryption = str(encryption).strip()
            if len(encryption) == 0:
                return 'iaas_vpn_create_109'

            algs = set(alg.strip() for alg in encryption.split(','))
            for alg in algs:
                if alg not in VPN.IKE_ENCRYPTION_ALGORITHMS:
                    return 'iaas_vpn_create_110'

            self.cleaned_data['ike_encryption'] = ','.join(algs)
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ike_encryption'] = VPN.AES256
        return None

    def validate_ike_lifetime(self, lifetime: Optional[int]) -> Optional[str]:
        """
        description: |
            The lifetime of the IKE phase in seconds.
            Must be a value between 180 and 86400 inclusive.
            Defaults to 28800.
        type: integer
        minimum: 180
        maximum: 86400
        """
        if lifetime is None:
            return None

        try:
            lifetime = int(lifetime)
        except (ValueError, TypeError):
            return 'iaas_vpn_create_111'

        if lifetime not in VPN.LIFETIME_RANGE:
            return 'iaas_vpn_create_112'

        self.cleaned_data['ike_lifetime'] = lifetime
        return None

    def validate_ike_pre_shared_key(self, pre_shared_key: Optional[str]) -> Optional[str]:
        """
        description: |
            The pre shared key to use for setting up the IKE phase of the VPN Tunnel.

            Note that the pre shared key cannot contain any of the following special characters;
            - `"`
            - `'`
            - `@`
            - `+`
            - `-`
            - `/`
            - `\\`
            - `|`
            - `=`

            It is set to CloudCIX defined key for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if pre_shared_key is None:
                pre_shared_key = ''
            pre_shared_key = str(pre_shared_key).strip()

            if len(pre_shared_key) == 0:
                return 'iaas_vpn_create_114'

            if SPECIAL_CHAR_PATTERN.search(pre_shared_key) is not None:
                return 'iaas_vpn_create_115'

            # Check the length
            elif len(pre_shared_key) > self.get_field('ike_pre_shared_key').max_length:
                return 'iaas_vpn_create_118'

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            # this field is not significant as Client doesn't need to know.
            pre_shared_key = 'SecureToVRVpn'

        self.cleaned_data['ike_pre_shared_key'] = pre_shared_key
        return None

    def validate_ike_version(self, version: Optional[str]) -> Optional[str]:
        """
        description: |
            String value of the chosen version for the IKE phase.

            The IKE phase versions supported by CloudCIX are;
            - `v1-only`
            - `v2-only`

            Please ensure the sent string matches one of these exactly.

            It is set to `v1-only` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if version is None:
                version = ''
            version = str(version).strip()

            if version not in IKE_VERSION_CHOICES:
                return 'iaas_vpn_create_122'

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            version = VPN.VERSION1

        self.cleaned_data['ike_version'] = version
        return None

    def validate_ipsec_authentication(self, authentication: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of authentication algorithms for the IPSec phase of the
            VPN Tunnel.

            The IPSec phase authentication algorithms supported by CloudCIX are;
            - `hmac-sha1-96`
            - `hmac-sha-256-128`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `hmac-sha-256-128` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if authentication is None:
                authentication = ''
            authentication = str(authentication).strip()
            if len(authentication) == 0:
                return 'iaas_vpn_create_123'

            auth_algs = set(alg.strip() for alg in authentication.split(','))
            for alg in auth_algs:
                if alg not in VPN.IPSEC_AUTHENTICATION_ALGORITHMS:
                    return 'iaas_vpn_create_124'

            self.cleaned_data['ipsec_authentication'] = ','.join(auth_algs)
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ipsec_authentication'] = VPN.HMAC_SHA256
        return None

    def validate_ipsec_encryption(self, encryption: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of encryption algorithms for the IPSEC phase of the VPN Tunnel.

            The IPSEC phase encryption algorithms supported by CloudCIX are;
            - `aes-128-cbc`
            - `aes-192-cbc`
            - `aes-256-cbc`
            - `aes-128-gcm`
            - `aes-192-gcm`
            - `aes-256-gcm`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `aes-256-gcm` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if encryption is None:
                encryption = ''
            encryption = str(encryption).strip()
            if len(encryption) == 0:
                return 'iaas_vpn_create_125'

            algs = set(alg.strip() for alg in encryption.split(','))
            for alg in algs:
                if alg not in VPN.IPSEC_ENCRYPTION_ALGORITHMS:
                    return 'iaas_vpn_create_126'
            self.cleaned_data['ipsec_encryption'] = ','.join(algs)

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ipsec_encryption'] = VPN.AES256G
        return None

    def validate_ipsec_establish_time(self, establish_time: Optional[str]) -> Optional[str]:
        """
        description: |
            String value of the chosen establish_time for the IPSec phase.

            The IPSec phase establish time values supported by CloudCIX are;
            - `immediately`
            - `on-traffic`

            Please ensure the sent string matches one of these exactly.

            It is set to `on-traffic` for Dynamic Secure connect type VPNs
        type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if establish_time is None:
                establish_time = ''
            establish_time = str(establish_time).strip()

            if establish_time not in IPSEC_ESTABLISH_CHOICES:
                return 'iaas_vpn_create_127'
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            establish_time = VPN.ESTABLISH_ON_TRAFFIC
        self.cleaned_data['ipsec_establish_time'] = establish_time
        return None

    def validate_ipsec_pfs_groups(self, pfs_groups: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of Perfect Forward Secrecy (PFS) groups for the IPSec phase of
            the VPN Tunnel.
            This can also be set to None

            The IPSec phase PFS groups supported by CloudCIX are;
            - `group1`
            - `group2`
            - `group5`
            - `group14`
            - `group19`
            - `group20`
            - `group24`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.

            It is set to `group19` for Dynamic Secure connect type VPNs
        type: string
        required: false
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] == VPN.SITE_TO_SITE:
            if pfs_groups is None:
                pfs_groups = ''
            pfs_groups = str(pfs_groups).strip()

            if len(pfs_groups) == 0:
                self.cleaned_data['ipsec_pfs_groups'] = ''
                return None

            groups = set(group.strip() for group in pfs_groups.split(','))
            for group in groups:
                if group not in VPN.PFS_GROUPS:
                    return 'iaas_vpn_create_128'

            self.cleaned_data['ipsec_pfs_groups'] = ','.join(groups)

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            self.cleaned_data['ipsec_pfs_groups'] = VPN.DH_GROUP_19
        return None

    def validate_ipsec_lifetime(self, lifetime: Optional[int]) -> Optional[str]:
        """
        description: |
            The lifetime of the IPSec phase in seconds.
            Must be a value between 180 and 86400 inclusive.
            Defaults to 3600.
        type: integer
        minimum: 180
        maximum: 86400
        """
        if lifetime is None:
            return None

        try:
            lifetime = int(lifetime)
        except (ValueError, TypeError):
            return 'iaas_vpn_create_129'

        if lifetime not in VPN.LIFETIME_RANGE:
            return 'iaas_vpn_create_130'

        self.cleaned_data['ipsec_lifetime'] = lifetime
        return None

    def validate_routes(self, routes: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of RoutesCreate objects to create the initial Route objects for the VPN.
        type: array
        items:
            type: object
            properties:
                local_subnet:
                    type: string
                remote_subnet:
                    type: string
        """
        routes = routes or []
        if not isinstance(routes, list):
            return 'iaas_vpn_create_131'

        if len(routes) == 0:
            return 'iaas_vpn_create_132'

        if 'virtual_router' not in self.cleaned_data or 'vpn_type' not in self.cleaned_data:
            return None

        # Create each of the route instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(routes))]
        instances: Deque[Route] = deque()

        for index, route in enumerate(routes):
            # route['virtual_router_id'] = self.cleaned_data['virtual_router'].pk
            route_controller = RouteCreateController(
                data=route,
                request=self.request,
                span=self.span,
                virtual_router=cast(VirtualRouter, self.cleaned_data['virtual_router']),
                vpn_id=None,
                vpn_type=self.cleaned_data['vpn_type'],
            )

            # Validate the controller
            if not route_controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = route_controller.errors
                continue

            # Add the instance to the instances deque
            route_controller.cleaned_data.pop('virtual_router')
            route_controller.cleaned_data.pop('vpn_type')
            instances.append(route_controller.instance)

        # Check if any route item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['routes'] = errors
            return None

        # If we make it here, then everything is fine
        self.cleaned_data['routes'] = instances
        return None

    def validate_traffic_selector(self, traffic_selector: Optional[bool]) -> Optional[str]:
        """
        description: |
            Boolean value stating if traffic selectors are to be used in configuring vpn tunnel. The default is false.

            By default, 0.0.0.0/0 will be used for the default local and remote subnets.
            If true, then each of the local and remote subnets will be added to the configuration negotiation with peer.
        type: boolean
        required: false
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if traffic_selector is None:
            traffic_selector = False
        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            traffic_selector = True
        if not isinstance(traffic_selector, bool):
            return 'iaas_vpn_create_133'

        self.cleaned_data['traffic_selector'] = traffic_selector
        return None

    def validate_vpn_clients(self, vpn_clients: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of VPNClientCreate objects to create the initial VPN Client objects for the
            Dynamic Secure Connect VPNs only.
        type: array
        items:
            type: object
            properties:
                password:
                    type: string
                username:
                    type: string
        """
        if 'vpn_type' not in self.cleaned_data:
            return None
        if self.cleaned_data['vpn_type'] != VPN.DYNAMIC_SECURE_CONNECT:
            return None
        vpn_clients = vpn_clients or []
        if not isinstance(vpn_clients, list):
            return 'iaas_vpn_create_138'

        if len(vpn_clients) == 0:
            return 'iaas_vpn_create_139'

        # Create each of the vpn_client instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(vpn_clients))]
        instances: Deque[VPNClient] = deque()

        for index, vpn_client in enumerate(vpn_clients):
            vpn_client_controller = VPNClientCreateController(
                data=vpn_client,
                request=self.request,
                span=self.span,
                vpn_id=None,
            )

            # Validate the controller
            if not vpn_client_controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = vpn_client_controller.errors
                continue

            # Add the instance to the instances deque
            instances.append(vpn_client_controller.instance)

        # Check if any vpn_client item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['vpn_clients'] = errors
            return None

        # If we make it here, then everything is fine
        self.cleaned_data['vpn_clients'] = instances
        return None


class VPNUpdateController(ControllerBase):
    """
    Validates User data used to create a VPN Tunnel
    """
    _instance: VPN
    subnet: Optional[netaddr.IPNetwork] = None

    class Meta(ControllerBase.Meta):
        """
        Override ControllerBase.Meta fields
        """
        model = VPN
        validation_order = (
            'description',
            'dns',
            'ike_authentication',
            'ike_dh_groups',
            'ike_gateway_type',
            'ike_gateway_value',
            'ike_encryption',
            'ike_lifetime',
            'ike_pre_shared_key',
            'ike_remote_identifier',
            'ike_version',
            'ipsec_authentication',
            'ipsec_encryption',
            'ipsec_establish_time',
            'ipsec_pfs_groups',
            'ipsec_lifetime',
            'traffic_selector',
            'routes',
            'vpn_clients',
        )

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        Extra handling of the errors property for handling the routes/vpn_clients errors in the case its a list
        """
        routes_popped = False
        clients_popped = False
        routes_errors = self._errors.get('routes', None)
        clients_errors = self._errors.get('vpn_clients', None)
        if isinstance(routes_errors, list):
            # Remove it, call super and add it back in
            routes_errors = self._errors.pop('routes')
            routes_popped = True
        if isinstance(clients_errors, list):
            # Remove it, call super and add it back in
            clients_errors = self._errors.pop('vpn_clients')
            clients_popped = True
        errors = super(VPNUpdateController, self).errors
        if routes_popped:
            errors['routes'] = routes_errors
        if clients_popped:
            errors['vpn_clients'] = clients_errors
        return errors

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: An optional description of what the vpn is for.
        type: string
        required: false
        """
        if description is None:
            description = self._instance.description
        else:
            description = str(description).strip()
        self.cleaned_data['description'] = description
        return None

    def validate_dns(self, dns: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP Address of the Customer's DNS.
            Must be IPv4 for now.
            Required only for Dynamic Secure connect VPN tunnels.
        type: string
        """
        if self._instance.vpn_type != VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if dns is None:
            ip = self._instance.dns
        else:
            try:
                ip = netaddr.IPAddress(dns)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_vpn_update_131'

            # For now, check that it is IPv4
            if ip.version != 4:
                return 'iaas_vpn_update_132'

        self.cleaned_data['dns'] = str(ip)
        return None

    def validate_ike_authentication(self, authentication: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of authentication algorithms for the IKE phase of the
            VPN Tunnel.

            The IKE phase authentication algorithms supported by CloudCIX are;
            - `sha1`
            - `sha-256`
            - `sha-384`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if authentication is None:
            authentication = ''
        authentication = str(authentication).strip()
        if len(authentication) == 0:
            return 'iaas_vpn_update_101'

        auth_algs = set(alg.strip() for alg in authentication.split(','))
        for alg in auth_algs:
            if alg not in VPN.IKE_AUTHENTICATION_ALGORITHMS:
                return 'iaas_vpn_update_102'

        self.cleaned_data['ike_authentication'] = ','.join(auth_algs)
        return None

    def validate_ike_dh_groups(self, dh_groups: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of Diffie-Helmen groups for the IKE phase of the VPN Tunnel.

            The IKE phase Diffie-Helmen groups supported by CloudCIX are;
            - `group1`
            - `group2`
            - `group5`
            - `group19`
            - `group20`
            - `group24`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if dh_groups is None:
            dh_groups = ''
        dh_groups = str(dh_groups).strip()
        if len(dh_groups) == 0:
            return 'iaas_vpn_update_103'

        groups = set(group.strip() for group in dh_groups.split(','))
        for group in groups:
            if group not in VPN.DH_GROUPS:
                return 'iaas_vpn_update_104'

        self.cleaned_data['ike_dh_groups'] = ','.join(groups)
        return None

    def validate_ike_gateway_type(self, ike_gateway_type: Optional[str]) -> Optional[str]:
        """
        description: |
            The type of data that is stored in the `ike_gateway_value` field.
            Can only be either "public_ip" or "hostname".
            Defaults to "public_ip".
        type: string
        """
        if ike_gateway_type is None:
            ike_gateway_type = self._instance.ike_gateway_type

        ike_gateway_type = str(ike_gateway_type).strip()

        if ike_gateway_type not in (VPN.GATEWAY_PUBLIC_IP, VPN.GATEWAY_HOSTNAME):
            return 'iaas_vpn_update_136'

        self.cleaned_data['ike_gateway_type'] = ike_gateway_type
        return None

    def validate_ike_gateway_value(self, ike_gateway_value: Optional[str]) -> Optional[str]:
        """
        description: |
            The value used as the IKE gateway for the VPN Tunnel.
            The type for this value depends on what type was set for the "ike_gateway_type" parameter.

            For "public_ip", this value must be a string containing an IPv4 address.
            For "hostname", this value must be a valid hostname.
        type: string
        """
        if ike_gateway_value is None:
            ike_gateway_value = self._instance.ike_gateway_value

        ike_gateway_value = str(ike_gateway_value).strip()

        if len(ike_gateway_value) == 0:
            return 'iaas_vpn_update_137'

        # Run different functions based on the type
        if self.cleaned_data.get('ike_gateway_type', self._instance.ike_gateway_type) == VPN.GATEWAY_PUBLIC_IP:
            return self._validate_ike_gateway_ip(ike_gateway_value)
        else:
            return self._validate_ike_gateway_fqdn(ike_gateway_value)

    def _validate_ike_gateway_ip(self, ike_gateway_value: str) -> Optional[str]:
        """
        Ensure the value is a valid IP. stolen from the old public ip validation
        """
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            # We don't need this value for DSC VPNs so just ignore it
            self.cleaned_data['ike_gateway_value'] = '0.0.0.0'
            return None

        # Otherwise, we validate it properly
        try:
            ip = netaddr.IPAddress(ike_gateway_value)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_vpn_update_116'

        # For now, check that it is IPv4
        if ip.version != 4:
            return 'iaas_vpn_update_117'

        self.cleaned_data['ike_gateway_value'] = str(ip)
        return None

    def _validate_ike_gateway_fqdn(self, ike_gateway_value: str) -> Optional[str]:
        """
        Ensure the value is a valid FQDN.
        """
        if len(ike_gateway_value) >= 253:
            return 'iaas_vpn_update_138'

        # Remove trailing dot
        if ike_gateway_value[-1] == '.':
            ike_gateway_value = ike_gateway_value[0:-1]

        #  Split ike_gateway_value into list of DNS labels
        labels = ike_gateway_value.split('.')

        # Check for existence of at least one '.' and all labels match that pattern.
        if len(labels) > 1 and all(FQDN_PATTERN.match(label) for label in labels):
            self.cleaned_data['ike_gateway_value'] = ike_gateway_value
            return None
        return 'iaas_vpn_update_138'

    def validate_ike_encryption(self, encryption: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of encryption algorithms for the IKE phase of the VPN Tunnel.

            The IKE phase encryption algorithms supported by CloudCIX are;
            - `aes-128-cbc`
            - `aes-192-cbc`
            - `aes-256-cbc`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if encryption is None:
            encryption = ''
        encryption = str(encryption).strip()
        if len(encryption) == 0:
            return 'iaas_vpn_update_105'

        algs = set(alg.strip() for alg in encryption.split(','))
        for alg in algs:
            if alg not in VPN.IKE_ENCRYPTION_ALGORITHMS:
                return 'iaas_vpn_update_106'

        self.cleaned_data['ike_encryption'] = ','.join(algs)
        return None

    def validate_ike_lifetime(self, lifetime: Optional[int]) -> Optional[str]:
        """
        description: |
            The lifetime of the IKE phase in seconds.
            Must be a value between 180 and 86400 inclusive.
            Defaults to 28800.
        type: integer
        minimum: 180
        maximum: 86400
        """
        if lifetime is None:
            return None

        try:
            lifetime = int(lifetime)
        except (ValueError, TypeError):
            return 'iaas_vpn_update_107'

        if lifetime not in VPN.LIFETIME_RANGE:
            return 'iaas_vpn_update_108'

        self.cleaned_data['ike_lifetime'] = lifetime
        return None

    def validate_ike_pre_shared_key(self, pre_shared_key: Optional[str]) -> Optional[str]:
        """
        description: |
            The pre shared key to use for setting up the IKE phase of the VPN Tunnel.

            Note that the pre shared key cannot contain any of the following special characters;
            - `"`
            - `'`
            - `@`
            - `+`
            - `-`
            - `/`
            - `\\`
            - `|`
            - `=`

        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if pre_shared_key is None:
            pre_shared_key = ''
        pre_shared_key = str(pre_shared_key).strip()

        if len(pre_shared_key) == 0:
            return 'iaas_vpn_update_110'

        if SPECIAL_CHAR_PATTERN.search(pre_shared_key) is not None:
            return 'iaas_vpn_update_111'

        # Check the length
        if len(pre_shared_key) > self.get_field('ike_pre_shared_key').max_length:
            return 'iaas_vpn_update_114'

        self.cleaned_data['ike_pre_shared_key'] = pre_shared_key
        return None

    def validate_ike_remote_identifier(self, ike_remote_identifier: str) -> Optional[str]:
        """
        description: |
            A string containing the value for the remote (Non-Project) IKE identifier for the VPN.
            It's default value is remote-<vpn_id>-<region_id>.<organisation_url> .
            Must be a valid FQDN of maximum char length 253
        type: string
        """
        if ike_remote_identifier in ['', None]:
            return 'iaas_vpn_update_139'

        if len(ike_remote_identifier) >= self.get_field('ike_remote_identifier').max_length:
            return 'iaas_vpn_update_140'

        # Remove trailing dot
        if ike_remote_identifier[-1] == '.':
            ike_remote_identifier = ike_remote_identifier[0:-1]

        #  Split ike_remote_identifier into list of DNS labels
        labels = ike_remote_identifier.split('.')

        # Check for existence of at least one '.' and all labels match that pattern.
        if len(labels) > 1 and all(FQDN_PATTERN.match(label) for label in labels):
            self.cleaned_data['ike_remote_identifier'] = ike_remote_identifier
            return None
        return 'iaas_vpn_update_141'

    def validate_ike_version(self, version: Optional[str]) -> Optional[str]:
        """
        description: |
            String value of the chosen version for the IKE phase.

            The IKE phase versions supported by CloudCIX are;
            - `v1-only`
            - `v2-only`

            Please ensure the sent string matches one of these exactly.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if version is None:
            version = ''
        version = str(version).strip()

        if version not in IKE_VERSION_CHOICES:
            return 'iaas_vpn_update_118'

        self.cleaned_data['ike_version'] = version
        return None

    def validate_ipsec_authentication(self, authentication: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of authentication algorithms for the IPSec phase of the
            VPN Tunnel.

            The IPSec phase authentication algorithms supported by CloudCIX are;
            - `hmac-sha1-96`
            - `hmac-sha-256-128`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if authentication is None:
            authentication = ''
        authentication = str(authentication).strip()
        if len(authentication) == 0:
            return 'iaas_vpn_update_119'

        auth_algs = set(alg.strip() for alg in authentication.split(','))
        for alg in auth_algs:
            if alg not in VPN.IPSEC_AUTHENTICATION_ALGORITHMS:
                return 'iaas_vpn_update_120'

        self.cleaned_data['ipsec_authentication'] = ','.join(auth_algs)
        return None

    def validate_ipsec_encryption(self, encryption: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of encryption algorithms for the IPSEC phase of the VPN Tunnel.

            The IPSEC phase encryption algorithms supported by CloudCIX are;
            - `aes-128-cbc`
            - `aes-192-cbc`
            - `aes-256-cbc`
            - `aes-128-gcm`
            - `aes-192-gcm`
            - `aes-256-gcm`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if encryption is None:
            encryption = ''
        encryption = str(encryption).strip()
        if len(encryption) == 0:
            return 'iaas_vpn_update_121'

        algs = set(alg.strip() for alg in encryption.split(','))
        for alg in algs:
            if alg not in VPN.IPSEC_ENCRYPTION_ALGORITHMS:
                return 'iaas_vpn_update_122'

        self.cleaned_data['ipsec_encryption'] = ','.join(algs)
        return None

    def validate_ipsec_establish_time(self, establish_time: Optional[str]) -> Optional[str]:
        """
        description: |
            String value of the chosen establish_time for the IPSec phase.

            The IPSec phase establish time values supported by CloudCIX are;
            - `immediately`
            - `on-traffic`

            Please ensure the sent string matches one of these exactly.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if establish_time is None:
            establish_time = ''
        establish_time = str(establish_time).strip()

        if establish_time not in IPSEC_ESTABLISH_CHOICES:
            return 'iaas_vpn_update_123'

        self.cleaned_data['ipsec_establish_time'] = establish_time
        return None

    def validate_ipsec_pfs_groups(self, pfs_groups: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing a comma separated array of Perfect Forward Secrecy (PFS) groups for the IPSec phase of
            the VPN Tunnel.
            This can also be set to None

            The IPSec phase PFS groups supported by CloudCIX are;
            - `group1`
            - `group2`
            - `group5`
            - `group14`
            - `group19`
            - `group20`
            - `group24`

            Please ensure that each entry in the array matches one of the above strings exactly.
            Duplicate entries will be ignored.
        type: string
        """
        # No updates here for Dynamic secure connect VPN type
        if self._instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            return None

        if pfs_groups is None:
            pfs_groups = ''
        pfs_groups = str(pfs_groups).strip()

        if len(pfs_groups) == 0:
            self.cleaned_data['ipsec_pfs_groups'] = ''
            return None

        groups = set(group.strip() for group in pfs_groups.split(','))
        for group in groups:
            if group not in VPN.PFS_GROUPS:
                return 'iaas_vpn_update_124'

        self.cleaned_data['ipsec_pfs_groups'] = ','.join(groups)
        return None

    def validate_ipsec_lifetime(self, lifetime: Optional[int]) -> Optional[str]:
        """
        description: |
            The lifetime of the IPSec phase in seconds.
            Must be a value between 180 and 86400 inclusive.
            Defaults to 3600.
        type: integer
        minimum: 180
        maximum: 86400
        """
        if lifetime is None:
            return None

        try:
            lifetime = int(lifetime)
        except (ValueError, TypeError):
            return 'iaas_vpn_update_125'

        if lifetime not in VPN.LIFETIME_RANGE:
            return 'iaas_vpn_update_126'

        self.cleaned_data['ipsec_lifetime'] = lifetime
        return None

    def validate_routes(self, routes: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of Route objects to apply as routes on the VPN.
        type: array
        items:
            type: object
            properties:
                local_subnet:
                    type: string
                remote_subnet:
                    type: string
        """
        routes = routes or []
        if not isinstance(routes, list):
            return 'iaas_vpn_update_127'

        if len(routes) == 0:
            return 'iaas_vpn_update_128'

        # Get a list of current routes
        current_route_ids = Route.objects.filter(
            deleted__isnull=True,
            vpn_id=self._instance.pk,
        ).values_list('pk', flat=True)
        updated_route_ids = []
        # Create each of the route instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(routes))]
        instances: Deque[Route] = deque()

        for index, data in enumerate(routes):
            pk = data.get('id', None)
            if pk is not None:
                updated_route_ids.append(pk)
                # Update Route
                try:
                    obj = Route.objects.get(id=pk)
                except Route.DoesNotExist:
                    return 'iaas_vpn_update_129'
                route_controller = RouteUpdateController(
                    data=data,
                    instance=obj,
                    request=self.request,
                    span=self.span,
                )
            else:
                # New route - create
                route_controller = RouteCreateController(
                    data=data,
                    request=self.request,
                    span=self.span,
                    virtual_router=cast(VirtualRouter, self._instance.virtual_router),
                    vpn_id=self._instance.pk,
                    vpn_type=self._instance.vpn_type,
                )

            # Validate the controller
            if not route_controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = route_controller.errors
                continue

            route_controller.cleaned_data.pop('virtual_router', None)
            route_controller.cleaned_data.pop('vpn_type', None)
            # Add the instance to the instances deque
            instances.append(route_controller.instance)

        # Check if any route item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['routes'] = errors
            return None

        # Any id in current_route_ids and not updates_route_ids are to be deleted.
        # We will only do this if no errors have been raised
        if len(self._errors) > 0:
            return None

        to_delete = list(set(current_route_ids) - set(updated_route_ids))

        if any(to_delete):
            Route.objects.filter(pk__in=to_delete).update(deleted=datetime.now())

        # If we make it here, then everything is fine
        self.cleaned_data['routes'] = instances
        return None

    def validate_traffic_selector(self, traffic_selector: Optional[bool]) -> Optional[str]:
        """
        description: |
            Boolean value stating if traffic selectors are to be used in configuring vpn tunnel. The default is false.

            By default, 0.0.0.0/0 will be used for the default local and remote subnets.
            If true, then each of the local and remote subnets will be added to the configuration negotiation with peer.
        type: boolean
        required: false
        """
        if traffic_selector is None:
            traffic_selector = self._instance.traffic_selector

        if not isinstance(traffic_selector, bool):
            return 'iaas_vpn_update_130'

        self.cleaned_data['traffic_selector'] = traffic_selector
        return None

    def validate_vpn_clients(self, vpn_clients: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of VPN Clients objects to apply as clients on the VPN.
        type: array
        items:
            type: object
            properties:
                password:
                    type: string
                username:
                    type: string
        """
        if self._instance.vpn_type != VPN.DYNAMIC_SECURE_CONNECT:
            return None
        vpn_clients = vpn_clients or []
        if not isinstance(vpn_clients, list):
            return 'iaas_vpn_update_133'

        if len(vpn_clients) == 0:
            return 'iaas_vpn_update_134'

        # Get a list of current vpn_clients
        current_vpn_client_ids = VPNClient.objects.filter(
            deleted__isnull=True,
            vpn_id=self._instance.pk,
        ).values_list('pk', flat=True)
        updated_vpn_client_ids = []
        # Create each of the vpn_client instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(vpn_clients))]
        instances: Deque[VPNClient] = deque()

        for index, data in enumerate(vpn_clients):
            pk = data.get('id', None)
            if pk is not None:
                updated_vpn_client_ids.append(pk)
                # Update VPNClient
                try:
                    obj = VPNClient.objects.get(id=pk)
                except VPNClient.DoesNotExist:
                    return 'iaas_vpn_update_135'
                vpn_client_controller = VPNClientUpdateController(
                    data=data,
                    instance=obj,
                    request=self.request,
                    span=self.span,
                )
            else:
                # New vpn_client - create
                vpn_client_controller = VPNClientCreateController(
                    data=data,
                    request=self.request,
                    span=self.span,
                    vpn_id=self._instance.pk,
                )
                self.cleaned_data['send_email'] = True

            # Validate the controller
            if not vpn_client_controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = vpn_client_controller.errors
                continue

            # Add the instance to the instances deque
            instances.append(vpn_client_controller.instance)

        # Check if any vpn_client item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['vpn_clients'] = errors
            return None

        # Any id in current_vpn_client_ids and not updates_vpn_client_ids are to be deleted.
        # We will only do this if no errors have been raised
        if len(self._errors) > 0:
            return None

        to_delete = list(set(current_vpn_client_ids) - set(updated_vpn_client_ids))

        if any(to_delete):
            VPNClient.objects.filter(pk__in=to_delete).update(deleted=datetime.now())

        # If we make it here, then everything is fine
        self.cleaned_data['vpn_clients'] = instances
        return None
