# stdlib
import re
from typing import Any, Dict, List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from iaas.models import (
    IPAddress,
    Router,
    Subnet,
)

__all__ = [
    'RouterCreateController',
    'RouterListController',
    'RouterUpdateController',
]

INTERFACE_REGEX = re.compile(r'[a-z0-9-\/]*$')


class RouterListController(ControllerBase):
    """
    Validates Router data used to filter a list of Routers
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        allowed_ordering = (
            'region_id',
            'asset_tag',
            'capacity',
            'created',
        )
        search_fields = {
            'asset_tag': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'capacity': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'enabled': (),
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class RouterCreateController(ControllerBase):
    """
    Validates Router data used to create a new Router record
    """

    class Meta(ControllerBase.Meta):
        model = Router
        validation_order = (
            'asset_tag',
            'capacity',
            'credentials',
            'enabled',
            'model',
            'username',
            'management_interface',
            'oob_interface',
            'public_interface',
            'private_interface',
            'router_oob_interface',
            'subnet_ids',
            'public_port_ips',
        )

    def validate_asset_tag(self, asset_tag: Optional[int]) -> Optional[str]:
        """
        description: CloudCIX Asset Tag for the Router. (Optional)
        required: false
        type: integer
        """
        if asset_tag is None:
            return None

        try:
            asset_tag = int(asset_tag)
        except (TypeError, ValueError):
            return 'iaas_router_create_101'

        self.cleaned_data['asset_tag'] = asset_tag
        return None

    def validate_capacity(self, capacity: Optional[int]) -> Optional[str]:
        """
        description: |
            The total number of Virtual Routers that this Router  can have built on it.

            If this value is None, then the Router can have an unlimited number of Virtual Routers built.
        nullable: true
        type: integer
        """
        if capacity is None:
            return None

        try:
            capacity = int(capacity)
        except (TypeError, ValueError):
            return 'iaas_router_create_102'

        self.cleaned_data['capacity'] = capacity
        return None

    def validate_credentials(self, credentials: Optional[str]) -> Optional[str]:
        """
        description : The credentials for a user with read only permissions to retrieve policy logs.
        type: string
        required: false
        """
        if credentials is None:
            return None
        credentials = str(credentials).strip()
        if len(credentials) > self.get_field('credentials').max_length:
            return 'iaas_router_create_103'

        self.cleaned_data['credentials'] = credentials
        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: A flag stating whether or not the Router is currently in use. (optional, defaults to True)
        required: false
        type: boolean
        """
        if enabled is None:
            enabled = True

        if enabled not in {True, False}:
            return 'iaas_router_create_104'

        self.cleaned_data['enabled'] = enabled
        return None

    def validate_model(self, model: Optional[str]) -> Optional[str]:
        """
        description : The Juniper SRX Model of the router.
        type: string
        """
        if model is None:
            model = ''
        model = str(model).strip()

        if len(model) == 0:
            return 'iaas_router_create_105'

        if len(model) > self.get_field('model').max_length:
            return 'iaas_router_create_106'

        self.cleaned_data['model'] = model
        return None

    def validate_username(self, username: Optional[str]) -> Optional[str]:
        """
        description : The username with read only permissions to retrieve policy logs.
        type: string
        required: false
        """
        if username is None:
            return None
        username = str(username).strip()
        if len(username) > self.get_field('username').max_length:
            return 'iaas_router_create_107'

        self.cleaned_data['username'] = username
        return None

    def validate_management_interface(self, management_interface: Optional[str]) -> Optional[str]:
        """
        description : The management_interface for router
        type: string
        required: false
        """
        if management_interface is None:
            return None
        management_interface = str(management_interface).strip().lower()
        if len(management_interface) > self.get_field('management_interface').max_length:
            return 'iaas_router_create_108'

        if INTERFACE_REGEX.match(management_interface) is None:
            return 'iaas_router_create_109'

        self.cleaned_data['management_interface'] = management_interface
        return None

    def validate_oob_interface(self, oob_interface: Optional[str]) -> Optional[str]:
        """
        description : The oob_interface for for the source/gateway of OOB network
        type: string
        required: false
        """
        if oob_interface is None:
            return None
        oob_interface = str(oob_interface).strip().lower()
        if len(oob_interface) > self.get_field('oob_interface').max_length:
            return 'iaas_router_create_110'

        if INTERFACE_REGEX.match(oob_interface) is None:
            return 'iaas_router_create_111'

        self.cleaned_data['oob_interface'] = oob_interface
        return None

    def validate_public_interface(self, public_interface: Optional[str]) -> Optional[str]:
        """
        description : The public_interface for router
        type: string
        required: false
        """
        if public_interface is None:
            return None
        public_interface = str(public_interface).strip().lower()
        if len(public_interface) > self.get_field('public_interface').max_length:
            return 'iaas_router_create_112'

        if INTERFACE_REGEX.match(public_interface) is None:
            return 'iaas_router_create_113'

        self.cleaned_data['public_interface'] = public_interface
        return None

    def validate_private_interface(self, private_interface: Optional[str]) -> Optional[str]:
        """
        description : The private_interface for router
        type: string
        required: false
        """
        if private_interface is None:
            return None
        private_interface = str(private_interface).strip().lower()
        if len(private_interface) > self.get_field('private_interface').max_length:
            return 'iaas_router_create_114'

        if INTERFACE_REGEX.match(private_interface) is None:
            return 'iaas_router_create_115'

        self.cleaned_data['private_interface'] = private_interface
        return None

    def validate_router_oob_interface(self, router_oob_interface: Optional[str]) -> Optional[str]:
        """
        description : The router_oob_interface is is a connection from oob network to router
        type: string
        required: false
        """
        if router_oob_interface is None:
            return None
        router_oob_interface = str(router_oob_interface).strip().lower()
        if len(router_oob_interface) > self.get_field('router_oob_interface').max_length:
            return 'iaas_router_create_116'

        if INTERFACE_REGEX.match(router_oob_interface) is None:
            return 'iaas_router_create_117'

        self.cleaned_data['router_oob_interface'] = router_oob_interface
        return None

    def validate_subnet_ids(self, subnet_ids: Optional[List[str]]) -> Optional[str]:
        """
        description: |
            Validate list of Subnet IDs to be configured on the router. There can only be one IPv6 /48 subnet
            configured. The first /64 will be the management subnet for the region. Each project in a region will be
            assigned a /64.
            There can be multiple IPv4 Subnets configured on the Router. The IPs from these subnets are Floating IPs
            for the Virtual Routers and VMs.
        type: List[str]
        """
        subnet_ids = subnet_ids or []

        if not isinstance(subnet_ids, list):
            return 'iaas_router_create_118'

        if len(subnet_ids) == 0:
            return 'iaas_router_create_119'

        ipv6_subnet = False
        router_subnets: List[Dict[str, Any]] = []

        for subnet_id in subnet_ids:
            try:
                subnet = Subnet.objects.get(pk=int(subnet_id), address_id=self.request.user.address['id'])
            except (TypeError, ValueError):
                return 'iaas_router_create_120'
            except Subnet.DoesNotExist:
                return 'iaas_router_create_121'

            network = netaddr.IPNetwork(subnet.address_range)

            if network.version == 6:
                # Ensure only 1 IPv6 subnet is sent in the request
                if ipv6_subnet:
                    return 'iaas_router_create_122'
                # Ensure it is a /48, netmask = `ffff:ffff:ffff::`
                if str(network.netmask) != 'ffff:ffff:ffff::':
                    return 'iaas_router_create_123'
                ipv6_subnet = True

            router_subnets.append(subnet)

        # Save so subnets can be updated with router_id if request is successful
        self.cleaned_data['router_subnets'] = router_subnets

        return None

    def validate_public_port_ips(self, public_port_ips: Optional[List[str]]) -> Optional[str]:
        """
        description: |
            Validate list of IP address to be assigned to the public port of the router.
        type: List[str]
        """
        public_port_ips = public_port_ips or []

        if not isinstance(public_port_ips, list):
            return 'iaas_router_create_124'

        if len(public_port_ips) == 0:
            return 'iaas_router_create_125'

        if 'router_subnets' not in self.cleaned_data:
            return None

        subnets = self.cleaned_data['router_subnets']

        ip_addresses: List[Dict[str, Any]] = []
        new_ips: List[str] = []

        for ip in public_port_ips:
            try:
                address = netaddr.IPAddress(ip)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_router_create_126'

            if address.is_private():
                return 'iaas_router_create_127'

            port_ip: Dict[str, Any] = {}
            for subnet in subnets:
                subnet_network = netaddr.IPNetwork(subnet.address_range)
                if address not in subnet_network:
                    continue

                if address in ([
                    subnet_network.network,     # Network Address
                    subnet_network.broadcast,   # Broadcast Address
                    subnet_network.ip,          # Gateway Address
                ]):
                    return 'iaas_router_create_128'

                # Check that address does not overlap with another ip in subnet
                existing = IPAddress.objects.filter(subnet=subnet).values_list('address', flat=True).iterator()

                existing = netaddr.IPSet(existing)
                if address in existing or address in new_ips:
                    return 'iaas_router_create_129'

                port_ip = {
                    'address': ip,
                    'name': f'Router IP region {self.request.user.address["id"]}',
                    'subnet': subnet,
                }

                break

            if 'subnet' not in port_ip:
                return 'iaas_router_create_130'

            ip_addresses.append(port_ip)
            new_ips.append(address)

        self.cleaned_data['public_port_ips'] = ip_addresses

        return None


class RouterUpdateController(ControllerBase):
    """
    Validates Router data used to update an existing Router
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = Router
        validation_order = (
            'asset_tag',
            'capacity',
            'credentials',
            'enabled',
            'model',
            'username',
            'management_interface',
            'oob_interface',
            'public_interface',
            'private_interface',
            'router_oob_interface',
            'subnet_ids',
            'public_port_ips',
        )

    def validate_asset_tag(self, asset_tag: Optional[int]) -> Optional[str]:
        """
        description: CloudCIX Asset Tag for the Router. (Optional)
        required: false
        type: integer
        """
        if asset_tag is None:
            return None

        try:
            asset_tag = int(asset_tag)
        except (TypeError, ValueError):
            return 'iaas_router_update_101'

        self.cleaned_data['asset_tag'] = asset_tag
        return None

    def validate_capacity(self, capacity: Optional[int]) -> Optional[str]:
        """
        description: |
            The total number of Virtual Routers that this Router  can have built on it.

            If this value is None, then the Router can have an unlimited number of Virtual Routers built.
        nullable: true
        type: integer
        """
        if capacity is None:
            return None

        try:
            capacity = int(capacity)
        except (TypeError, ValueError):
            return 'iaas_router_update_102'

        self.cleaned_data['capacity'] = capacity
        return None

    def validate_credentials(self, credentials: Optional[str]) -> Optional[str]:
        """
        description : The credentials for a user with read only permissions to retrieve policy logs.
        type: string
        required: false
        """
        if credentials is None:
            return None
        credentials = str(credentials).strip()
        if len(credentials) > self.get_field('credentials').max_length:
            return 'iaas_router_update_103'

        self.cleaned_data['credentials'] = credentials
        return None

    def validate_enabled(self, enabled: Optional[bool]) -> Optional[str]:
        """
        description: A flag stating whether or not the Router is currently in use. (optional, defaults to True)
        required: false
        type: boolean
        """
        if enabled is None:
            return None

        if enabled not in {True, False}:
            return 'iaas_router_update_104'

        self.cleaned_data['enabled'] = enabled
        return None

    def validate_model(self, model: Optional[str]) -> Optional[str]:
        """
        description : The Juniper SRX Model of the router.
        type: string
        """
        if model is None:
            model = self._instance.model
        model = str(model).strip()

        if len(model) == 0:
            return 'iaas_router_update_105'

        if len(model) > self.get_field('model').max_length:
            return 'iaas_router_update_106'

        self.cleaned_data['model'] = model
        return None

    def validate_username(self, username: Optional[str]) -> Optional[str]:
        """
        description : The username with read only permissions to retrieve policy logs.
        type: string
        required: false
        """
        if username is None:
            return None
        username = str(username).strip()
        if len(username) > self.get_field('username').max_length:
            return 'iaas_router_update_107'

        self.cleaned_data['username'] = username
        return None

    def validate_management_interface(self, management_interface: Optional[str]) -> Optional[str]:
        """
        description : The management_interface for router
        type: string
        required: false
        """
        if management_interface is None:
            return None
        management_interface = str(management_interface).strip().lower()
        if len(management_interface) > self.get_field('management_interface').max_length:
            return 'iaas_router_update_108'

        if INTERFACE_REGEX.match(management_interface) is None:
            return 'iaas_router_update_109'

        self.cleaned_data['management_interface'] = management_interface
        return None

    def validate_oob_interface(self, oob_interface: Optional[str]) -> Optional[str]:
        """
        description : The oob_interface for router
        type: string
        required: false
        """
        if oob_interface is None:
            return None
        oob_interface = str(oob_interface).strip().lower()
        if len(oob_interface) > self.get_field('oob_interface').max_length:
            return 'iaas_router_update_110'

        if INTERFACE_REGEX.match(oob_interface) is None:
            return 'iaas_router_update_111'

        self.cleaned_data['oob_interface'] = oob_interface
        return None

    def validate_public_interface(self, public_interface: Optional[str]) -> Optional[str]:
        """
        description : The public_interface for router
        type: string
        required: false
        """
        if public_interface is None:
            return None
        public_interface = str(public_interface).strip().lower()
        if len(public_interface) > self.get_field('public_interface').max_length:
            return 'iaas_router_update_112'

        if INTERFACE_REGEX.match(public_interface) is None:
            return 'iaas_router_update_113'

        self.cleaned_data['public_interface'] = public_interface
        return None

    def validate_private_interface(self, private_interface: Optional[str]) -> Optional[str]:
        """
        description : The private_interface for router
        type: string
        required: false
        """
        if private_interface is None:
            return None
        private_interface = str(private_interface).strip().lower()
        if len(private_interface) > self.get_field('private_interface').max_length:
            return 'iaas_router_update_114'

        if INTERFACE_REGEX.match(private_interface) is None:
            return 'iaas_router_update_115'

        self.cleaned_data['private_interface'] = private_interface
        return None

    def validate_router_oob_interface(self, router_oob_interface: Optional[str]) -> Optional[str]:
        """
        description : The router_oob_interface for router
        type: string
        required: false
        """
        if router_oob_interface is None:
            return None
        router_oob_interface = str(router_oob_interface).strip().lower()
        if len(router_oob_interface) > self.get_field('router_oob_interface').max_length:
            return 'iaas_router_update_116'

        if INTERFACE_REGEX.match(router_oob_interface) is None:
            return 'iaas_router_update_117'

        self.cleaned_data['router_oob_interface'] = router_oob_interface
        return None

    def validate_subnet_ids(self, subnet_ids: Optional[List[str]]) -> Optional[str]:
        """
        description: |
            Validate list of Subnet IDs to be configured on the router. There can only be one IPv6 /48 subnet
            configured. The first /64 will be the management subnet for the region. Each project in a region will be
            assigned a /64.
            There can be multiple IPv4 Subnets configured on the Router. The IPs from these subnets are Floating IPs
            for the Virtual Routers and VMs.
        type: List[str]
        """
        if subnet_ids is None:
            return None

        if not isinstance(subnet_ids, list):
            return 'iaas_router_update_118'

        if len(subnet_ids) == 0:
            return 'iaas_router_update_119'

        configured_subnets = Subnet.objects.filter(router=self._instance).values_list('pk', flat=True)

        remove_subnets = [sub for sub in configured_subnets if sub not in subnet_ids]
        add_subnets = [sub for sub in subnet_ids if sub not in configured_subnets]
        subnets = [sub for sub in subnet_ids if sub in configured_subnets]

        ipv6_subnet = False
        region_id = self._instance.region_id

        router_subnets: List[Subnet] = []
        for subnet_id in subnets:
            subnet: Subnet = Subnet.objects.get(pk=subnet_id)
            network = netaddr.IPNetwork(subnet.address_range)
            if network.version == 6:
                ipv6_subnet = True
            router_subnets.append(subnet)

        for subnet_id in remove_subnets:
            # Ensure there are no cloud child subnets
            if Subnet.objects.filter(parent_id=subnet_id, cloud=True).exists():
                return 'iaas_router_update_120'
            # Ensure there are no cloud ip addresses in use
            if IPAddress.objects.filter(subnet_id=subnet_id, cloud=True).exists():
                return 'iaas_router_update_121'
            subnet = Subnet.objects.get(pk=int(subnet_id), address_id=region_id)
            network = netaddr.IPNetwork(subnet.address_range)

        for subnet_id in add_subnets:
            try:
                subnet = Subnet.objects.get(pk=int(subnet_id), address_id=region_id)
            except (TypeError, ValueError):
                return 'iaas_router_update_122'
            except Subnet.DoesNotExist:
                return 'iaas_router_update_123'

            network = netaddr.IPNetwork(subnet.address_range)
            if network.version == 6:
                # Ensure only 1 IPv6 subnet assigned to router
                if ipv6_subnet:
                    return 'iaas_router_update_124'
                # Ensure it is a /48, netmask = `ffff:ffff:ffff::`
                if str(network.netmask) != 'ffff:ffff:ffff::':
                    return 'iaas_router_update_125'

                ipv6_subnet = True
            router_subnets.append(subnet)

        # Save so subnets can be updated with router_id changes if request is successful
        self.cleaned_data['router_subnets'] = router_subnets
        self.cleaned_data['remove_subnets'] = remove_subnets

        return None

    def validate_public_port_ips(self, public_port_ips: Optional[List[str]]) -> Optional[str]:
        """
        description: |
            Validate list of IP address to be assigned to the public port of the router.
        type: List[str]
        """
        if public_port_ips is None:
            return None

        if not isinstance(public_port_ips, list):
            return 'iaas_router_update_126'

        if len(public_port_ips) == 0:
            return 'iaas_router_update_127'

        if 'router_subnets' not in self.cleaned_data:
            return None

        subnets = self.cleaned_data['router_subnets']

        region_id = self._instance.region_id

        ip_addresses: List[Dict[str, Any]] = []
        new_ips: List[str] = []

        current_ips = list(self._instance.router_ips.values_list('address', flat=True).iterator())
        current_ips = netaddr.IPSet(current_ips)

        for ip in public_port_ips:
            try:
                address = netaddr.IPAddress(ip)
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_router_update_128'

            if address.is_private():
                return 'iaas_router_update_129'

            port_ip: Dict[str, Any] = {}
            for subnet in subnets:
                subnet_network = netaddr.IPNetwork(subnet.address_range)
                if address not in subnet_network:
                    continue

                if address in ([
                    subnet_network.network,     # Network Address
                    subnet_network.broadcast,   # Broadcast Address
                    subnet_network.ip,          # Gateway Address
                ]):
                    return 'iaas_router_update_130'

                # Check that address does not overlap with another ip in subnet
                existing = IPAddress.objects.filter(subnet=subnet).values_list('address', flat=True).iterator()

                existing = netaddr.IPSet(existing)
                if address in existing or address in new_ips:
                    if address not in current_ips:
                        return 'iaas_router_update_131'

                port_ip = {
                    'address': ip,
                    'name': f'Router IP region {region_id}',
                    'subnet': subnet,
                }

                break

            if 'subnet' not in port_ip:
                return 'iaas_router_update_132'

            ip_addresses.append(port_ip)
            new_ips.append(address)

        self.cleaned_data['public_port_ips'] = ip_addresses

        return None
