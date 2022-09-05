# stdlib
from collections import deque
from typing import Any, cast, Deque, Dict, List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from cloudcix_rest.utils import get_error_details
from django.conf import settings
from jaeger_client import Span
# local
from iaas import models, state, skus
from ..firewall_rule import FirewallRuleCreateController
from ..helpers import create_cloud_subnets, get_stif_number, IAASException
from ..project import ProjectCreateController
from ..virtual_router import VirtualRouterUpdateController
from ..vm import VMCreateController
from ..vpn import VPNCreateController


__all__ = [
    'CloudCreateController',
    'CloudCreateException',
    'VPNCreateException',
]


class CloudCreateException(Exception):
    """For exceptions from the _create_* methods"""
    response: Dict[str, Any]

    def __init__(self, response: Dict[str, Any]) -> None:
        self.response = response


class VPNCreateException(Exception):
    pass


class CloudCreateController(ControllerBase):
    """
    Validates Cloud data used to create an entire Cloud Project safely.
    """

    # Instance variables of every cloud item
    firewall_rules: Deque[models.FirewallRule]
    project: Optional[models.Project] = None
    virtual_router: Optional[models.VirtualRouter] = None
    vms: Deque[models.VM]
    vpns: Deque[models.VPN]

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        validation_order = (
            'project',
            'subnets',
            'vms',
            'vpns',
            'firewall_rules',
        )

    def __init__(self, *args, **kwargs) -> None:
        super(CloudCreateController, self).__init__(*args, **kwargs)
        self.firewall_rules = deque()
        self.vms = deque()
        self.vpns = deque()

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        If the user requests errors, delete all the objects.

        Then, potentially check for modifications that need to be made to error fields.
        """
        # Delete objects
        for firewall in self.firewall_rules:
            firewall.delete()
        for vpn in self.vpns:
            models.Route.objects.filter(vpn_id=vpn.pk).delete()
            if vpn.vpn_type == models.VPN.DYNAMIC_SECURE_CONNECT:
                models.VPNClient.objects.filter(vpn_id=vpn.pk).delete()
            models.VPNHistory.objects.filter(vpn_id=vpn.pk).delete()
            vpn.delete()
        for vm in self.vms:
            models.StorageHistory.objects.filter(vm_history__vm_id=vm.pk).delete()
            models.VMHistory.objects.filter(vm_id=vm.pk).delete()
            models.IPAddress.objects.filter(vm_id=vm.pk).delete()
            vm.delete()
        if self.virtual_router is not None:
            self.virtual_router.set_deleted()
            self.virtual_router.delete()
        if self.project is not None:
            self.project.delete()

        # Handle any necessary modifications to the errors dict that needs to be made
        errors = {}
        for field, error in self._errors.items():
            if isinstance(error, str):
                error = get_error_details(error)[error]
            errors[field] = error
        return errors

    def save(self):
        """
        If this method is called, go through the objects that have states and set them to 1
        """
        if self.virtual_router is not None:  # It won't be if we call this method, this is just for mypy
            self.virtual_router.state = state.REQUESTED
            self.virtual_router.save()
        for vm in self.vms:
            vm.state = state.REQUESTED
            vm.save()
        self.project.run_icarus = True
        self.project.run_robot = True
        self.project.save()

    def validate_project(self, project: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        $ref: '#/components/schemas/ProjectCreate'
        """
        if project is None:
            return 'iaas_cloud_create_101'

        if not isinstance(project, dict):
            return 'iaas_cloud_create_102'

        # Pass the sent data into the Project Controller
        controller = ProjectCreateController(
            request=self.request,
            data=project,
            span=self.span,
        )
        if not controller.is_valid():
            self._errors['project'] = controller.errors
            return None

        # Save the Project, creating all the extra necessary things
        errors = controller.save(self.span)
        if errors is not None:
            self._errors['project'] = errors.get('errors', errors)
            return None

        self.project = controller.instance
        self.project.save()
        self.virtual_router = controller.instance.virtual_router
        self.virtual_router.state = state.IN_API

        return None

    def validate_subnets(self, subnets: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects containing details of the Subnets to be created in the Virtual Router for this Project
        type: array
        items:
            type: object
            properties:
                address_range:
                    description: |
                        The CIDR notation for the address range of the Subnet.

                        The sent address will be used as the gateway, so this value can not match the network or
                        broadcast addresses. For example; 10.0.0.1/24 is okay but 10.0.0.0/24 is not.
                    type: string
                name:
                    description: A verbose name used to identify the Subnet
                    type: string
        """
        # Check that we have a virtual router before going forward
        if self.virtual_router is None:  # pragma: no cover
            return None

        subnets = subnets or []
        data = {'subnets': subnets}

        controller = VirtualRouterUpdateController(
            request=self.request,
            data=data,
            span=self.span,
            instance=self.virtual_router,
        )
        if not controller.is_valid():
            self._errors['subnets'] = controller.errors
            return None

        # Save the subnets temporarily as well
        subs = controller.cleaned_data.pop('subnets', {})

        if subs is not None:
            try:
                create_cloud_subnets(
                    self.request,
                    self.project,
                    subs,
                    'iaas_cloud_create_103',
                    span=self.span,
                )
            except IAASException as e:  # pragma: no cover
                self._errors['subnets'] = e.args[0]
                return None

        return None

    def validate_vms(self, vms: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects containing the details of the VMs to be built in the Project
        type: array
        items:
            type: object
            required:
                - image_id
                - storage_type_id
                - storages
                - cpu
                - ram
                - dns
                - name
                - gateway_subnet
                - ip_addresses
            properties:
                image_id:
                    description: The ID of the Image that will be used to build the VM.
                    type: integer
                storage_type_id:
                    description: |
                        The ID of the StorageType that will be used in the VM
                    type: integer
                storages:
                    description: |
                        An array of StorageCreate objects to create the initial Storage objects for the VM.
                    type: array
                    items:
                        $ref: '#/components/schemas/StorageCreate'
                cpu:
                    description: |
                        The number of Virtual CPUs (vCPUs) that the VM should be created with.
                    type: integer
                ram:
                    description: |
                        The amount of RAM (in GB) that the VM should be created with.
                    type: integer
                dns:
                    description: |
                        A string containing IP Addresses, separated by commas, that represent the DNS servers that the
                        VM will use.
                    type: string
                name:
                    description: |
                        A verbose name for the VM. Must be unique within a Project.
                    type: string
                gateway_subnet:
                    description: |
                        An optional subnet address range. Must be an address range from the sent subnets. Only
                        IP addresses from this subnet can be NATed to a floating IP Address.
                    type: string
                ip_addresses:
                    description: |
                        An array of Private IP Addresses for the VM.
                    type: array
                    properties:
                        address:
                            description: A private IP address for the VM.
                            type: string
                        nat:
                            description: Should the private IP address be NATed to a floating IP address.
                            type: boolean
        """
        # Initial checking of the sent data before running creation jobs
        vms = vms or []
        if not isinstance(vms, list):
            return 'iaas_cloud_create_104'
        if len(vms) == 0:
            return 'iaas_cloud_create_105'

        # We need virtual router to progress
        if self.virtual_router is None:  # pragma: no cover
            return None

        tracer = settings.TRACER

        # Set up a list of errors
        errors: List[Optional[Dict[str, Any]]] = [None for _ in vms]

        # Iterate through the list and attempt to create each VM in question
        for index, data in enumerate(vms):
            if not isinstance(data, dict):
                code = 'iaas_cloud_create_106'
                errors[index] = get_error_details(code)[code]
                continue

            try:
                with tracer.start_span(f'_create_vm_{index}', child_of=self.span) as span:
                    self.vms.append(self._create_vm(data, span))
            except CloudCreateException as e:
                errors[index] = e.response

        # Check if we have errors to report
        if any(error is not None for error in errors):
            self._errors['vms'] = errors

        # We add the vms to self.vms immediately after creation because we need to know what to delete in case
        # of errors, so we don't have to do anything here
        return None

    def validate_vpns(self, vpns: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects containing the details of VPN Tunnels to be built for the Project
        type: array
        required: false
        items:
            type: object
            required:
                - dns
                - ike_authentication
                - ike_dh_groups
                - ike_encryption
                - ike_lifetime
                - ike_mode
                - ike_pre_shared_key
                - ike_version
                - ipsec_authentication
                - ipsec_encryption
                - ipsec_establish_time
                - ipsec_pfs_groups
                - ipsec_lifetime
                - routes
                - traffic_selector
                - vpn_clients
            properties:
                dns:
                    description: |
                        The IP Address of the Customer's DNS.
                        Must be IPv4 for now.
                        Required only for Dynamic Secure connect type VPNs.
                    type: string
                ike_authentication:
                    description: |
                        A string containing a comma separated array of authentication algorithms for the IKE phase of
                        the VPN Tunnel.

                        The IKE phase authentication algorithms supported by CloudCIX are;
                        - `md5`
                        - `sha1`
                        - `sha-256`
                        - `sha-384`

                        Please ensure that each entry in the array matches one of the above strings exactly.
                        Duplicate entries will be ignored.

                        It is set to `sha-256` for Dynamic Secure connect type VPNs
                    type: string
                ike_dh_groups:
                    description: |
                        A string containing a comma separated array of Diffie-Helmen groups for the IKE phase of the
                        VPN Tunnel.

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
                ike_encryption:
                    description: |
                        A string containing a comma separated array of encryption algorithms for the IKE phase of the
                        VPN Tunnel.

                        The IKE phase encryption algorithms supported by CloudCIX are;
                        - `aes-128-cbc`
                        - `aes-192-cbc`
                        - `aes-256-cbc`
                        - `des-cbc`
                        - `3des-cbc`

                        Please ensure that each entry in the array matches one of the above strings exactly.
                        Duplicate entries will be ignored.

                        It is set to `aes-256-cbc` for Dynamic Secure connect type VPNs
                    type: string
                ike_lifetime:
                    description: |
                        The lifetime of the IKE phase in seconds.
                        Must be a value between 180 and 86400 inclusive.
                        Defaults to 28800.
                    minimum: 180
                    maximum: 86400
                    type: integer
                ike_mode:
                    description: |
                        String value of the chosen mode for the IKE phase.

                        The IKE phase modes supported by CloudCIX are;
                        - `main`
                        - `aggressive`

                        Please ensure the sent string matches one of these exactly.

                        It is set to `aggressive` for Dynamic Secure connect type VPNs
                    type: string
                ike_pre_shared_key:
                    description: |
                        The pre shared key to use for setting up the IKE phase of the VPN Tunnel.

                        Note that the pre shared key cannot contain any of the following special characters;
                        - "
                        - '
                        - @
                        - +
                        - -
                        - /
                        - \
                        - |
                        - =

                        Also note that the default max length of the pre shared key is 255 characters, except in the
                        following cases;
                        - If the chosen IKE encryption algorithm is `des-cbc`, the max length is 8 characters
                        - If the chosen IKE encryption algorithm is `3des-cbc`, the max length is 24 characters

                        It is set to CloudCIX defined key for Dynamic Secure connect type VPNs
                    type: string
                ike_version:
                    description: |
                        String value of the chosen version for the IKE phase.

                        The IKE phase versions supported by CloudCIX are;
                        - `v1-only`
                        - `v2-only`

                        Please ensure the sent string matches one of these exactly.

                        It is set to `v1-only` for Dynamic Secure connect type VPNs
                    type: string
                ipsec_authentication:
                    description: |
                        A string containing a comma separated array of authentication algorithms for the IPSec phase of
                        the VPN Tunnel.

                        The IPSec phase authentication algorithms supported by CloudCIX are;
                        - `hmac-md5-96`
                        - `hmac-sha1-96`
                        - `hmac-sha-256-128`

                        Please ensure that each entry in the array matches one of the above strings exactly.
                        Duplicate entries will be ignored.

                        It is set to `hmac-sha-256-128` for Dynamic Secure connect type VPNs
                    type: string
                ipsec_encryption:
                    description: |
                        A string containing a comma separated array of encryption algorithms for the IPSEC phase of
                        the VPN Tunnel.

                        The IPSEC phase encryption algorithms supported by CloudCIX are;
                        - `aes-128-cbc`
                        - `aes-192-cbc`
                        - `aes-256-cbc`
                        - `des-cbc`
                        - `3des-cbc`
                        - `aes-128-gcm`
                        - `aes-192-gcm`
                        - `aes-256-gcm`

                        Please ensure that each entry in the array matches one of the above strings exactly.
                        Duplicate entries will be ignored.

                        It is set to `aes-256-cbc` for Dynamic Secure connect type VPNs
                    type: string
                ipsec_establish_time:
                    description: |
                        String value of the chosen establish_time for the IPSec phase.

                        The IPSec phase establish time values supported by CloudCIX are;
                        - `immediately`
                        - `on-traffic`

                        Please ensure the sent string matches one of these exactly.

                        It is set to `on-traffic` for Dynamic Secure connect type VPNs
                    type: string
                ipsec_pfs_groups:
                    description: |
                        A string containing a comma separated array of Perfect Forward Secrecy (PFS) groups for the
                        IPSec phase of the VPN Tunnel.
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
                ipsec_lifetime:
                    description: |
                        The lifetime of the IPSec phase in seconds.
                        Must be a value between 180 and 86400 inclusive.
                        Defaults to 3600.
                    minimum: 180
                    maximum: 86400
                    type: integer
                routes:
                    description: |
                        An array of routes with local and remote subnets to connect via the VPN.

                        The local subnet is the CIDR of the Subnet in the Project that this Route will connect with.
                        The remote subnet is the CIDR of the Subnet on the Customer side of the VPN Tunnel that should
                        be given access through the Route.

                        Please note that none of the remote subnets can overlap with any of the Subnets in this Project
                        or with a remote subnet on another VPN's route in this Project.

                    items:
                        type: object
                        properties:
                            local_subnet:
                                type: string
                            remote_subnet:
                                type: string
                traffic_selector:
                    description: |
                        Boolean value stating if traffic selectors are to be used in configuring vpn tunnel.
                        The default is false and 0.0.0.0/0 will be used for the default local and remote subnets.
                        If true, then each of the local and remote subnets will be added to the configuration
                        negotiation with peer.
                    type: boolean
                vpn_clients:
                    description: |
                        An array of vpn_clients with username and passwords to connect Dynamic Secure connect VPNtunnel.

                    items:
                        type: object
                        properties:
                            password:
                                description:
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
                            username:
                                description:
                                    Note that the username cannot contain any of the following special characters;
                                    - `"`
                                    - `&`
                                    - `(`
                                    - `)`
                                    - `\\`
                                    - `|`
                                    - `?`

                                    Also note that the default max length of the username is 64 characters.
                                type: string
        """
        # Initial checking of the sent data before running creation jobs
        vpns = vpns or []
        if not isinstance(vpns, list):
            return 'iaas_cloud_create_107'

        # Early out, don't need to do setup for a project with no vpns
        if len(vpns) == 0:
            return None

        # If there are no subnets, return out here since the requests will definitely fail
        if self.virtual_router is None:  # pragma: no cover
            return None

        tracer = settings.TRACER

        # Set up a list of errors
        errors: List[Optional[Dict[str, Any]]] = [None for _ in vpns]

        subnets = models.Subnet.objects.filter(virtual_router_id=self.virtual_router.pk)

        # Build up a map of subnets
        subnets = {subnet.address_range: subnet.pk for subnet in subnets}

        # Iterate through the list and attempt to create each VPN in question
        for index, data in enumerate(vpns):
            if not isinstance(data, dict):
                code = 'iaas_cloud_create_108'
                errors[index] = get_error_details(code)[code]
                continue

            # If we have it, run the controller
            try:
                with tracer.start_span(f'_create_vpn_{index}', child_of=self.span) as span:
                    self.vpns.append(self._create_vpn(data, span))
            except CloudCreateException as e:
                errors[index] = e.response
            except VPNCreateException as e:  # pragma: no cover
                errors[index] = {'stif_number': get_error_details(e.args[0])[e.args[0]]}

        # Check if we have errors to report
        if any(error is not None for error in errors):
            self._errors['vpns'] = errors

        # We add the vpns to self.vpns immediately after creation because we need to know what to delete in case
        # of errors, so we don't have to do anything here
        return None

    def validate_firewall_rules(self, firewall_rules: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects representing Firewall Rules to be created in the Virtual Router.

            Any existing Firewall Rules will be removed before creating the ones contained in this request.
            There is no way to create or update a single Firewall Rule record currently, so they can only be managed
            through the Cloud endpoints.
        type: array
        required: false
        items:
            type: object
            required:
                - allow
                - source
                - destination
                - port
                - protocol
            properties:
                allow:
                    description: |
                        A flag that states whether traffic matching this rule should be allowed to pass through the
                        firewall
                    type: boolean
                source:
                    description: |
                        A Subnet or IP Address that indicates what the source of traffic should be in order to match
                        this rule.
                        Can also be just a `*` character, which will indicate that any source is allowed.

                        Please note that out of source and destination, one must be a public range and the other must
                        be a private range.
                        Also, both source and destination must use the same IP Version.
                    type: string
                destination:
                    description: |
                        A Subnet or IP Address that indicates what the destination of traffic should be in order to
                        match this rule.
                        Can also be just a `*` character, which will indicate that any destination is allowed.

                        Please note that out of source and destination, one must be a public range and the other must
                        be a private range.
                        Also, both source and destination must use the same IP Version.
                    type: string
                port:
                    description: |
                        An string containing an integer that indicates what the destination port of traffic should be
                        in order to match this rule.
                        Can also be just a `*` character, which will indicate that any port is allowed.

                        If an integer port is supplied, it must be in the range of 1 - 65535 inclusive.
                    type: string
                    pattern: '^(\\*|[0-9]{1,5})$'
                protocol:
                    description: |
                        A string that indicates what protocol traffic should be using in order to match this rule.
                        The currently supported protocols are as following;
                            - 'tcp'
                            - 'udp'

                        The special case protocol 'any' is allowed when the '*' character is sent for port, and allows
                        any protocol through in these situations.
                        This is to allow the user to set up rules in the firewall that allow all traffic through, if
                        they don't care about having a firewall for their project.
                    type: string
                description:
                    description: An optional description of what the rule is for.
                    type: string
        """
        # Initial checking of the sent data before running creation jobs
        firewall_rules = firewall_rules or []
        if not isinstance(firewall_rules, list):
            return 'iaas_cloud_create_109'

        # Early out, don't need to do setup for a project with no firewall_rules
        if len(firewall_rules) == 0:
            return None

        # If there are no subnets, return out here since the requests will definitely fail
        if self.virtual_router is None:  # pragma: no cover
            return None

        tracer = settings.TRACER

        # Set up a list of errors
        errors: List[Optional[Dict[str, Any]]] = [None for _ in firewall_rules]

        # Iterate through the list and attempt to create each VM in question
        for index, data in enumerate(firewall_rules):
            if not isinstance(data, dict):
                code = 'iaas_cloud_create_110'
                errors[index] = get_error_details(code)[code]
                continue

            try:
                with tracer.start_span(f'_create_firewall_rule_{index}', child_of=self.span) as span:
                    self.firewall_rules.append(self._create_firewall_rule(data, index, span))
            except CloudCreateException as e:
                errors[index] = e.response

        # Check if we have errors to report
        if any(error is not None for error in errors):
            self._errors['firewall_rules'] = errors

        # Refresh the virtual router again to access the Firewall Rules
        cast(models.VirtualRouter, self.virtual_router).refresh_from_db()

        # We add the firewall_rules to self.firewall_rules immediately after creation because we need to know what to
        # delete in case of errors, so we don't have to do anything here
        return None

    def _create_vm(self, data: Dict[str, Any], span: Span) -> models.VM:
        """
        Create a VM using the Controller and the supplied data.
        This has been put into its own method so that the update controller can also use it.

        Also creates the necessary Storages / History objects
        """
        tracer = settings.TRACER

        # Need to add the Project ID to the data
        data['project_id'] = cast(models.Project, self.project).id

        with tracer.start_span('validating_controller', child_of=span) as child_span:
            controller = VMCreateController(
                request=self.request,
                data=data,
                span=child_span,
            )
            if not controller.is_valid():
                raise CloudCreateException(controller.errors)

        # Save the object
        with tracer.start_span('saving_object', child_of=span):
            storages = controller.cleaned_data.pop('storages')
            ip_addresses = controller.cleaned_data.pop('ip_addresses', [])
            controller.instance.save()

        # Create IP Addresses for VM
        with tracer.start_span('saving_vm_ips', child_of=self.span):
            for ip in ip_addresses:
                models.IPAddress.objects.create(
                    cloud=True,
                    vm=controller.instance,
                    modified_by=self.request.user.id,
                    **ip,
                )

        # Handle Storages / History / etc
        storage_history: List[Dict[str, Any]] = []
        with tracer.start_span('saving_storages', child_of=span):
            instances = []
            storage_type_sku = controller.vm_history.pop('storage_type_sku')
            for storage in storages:
                item: Dict[str, Any] = {}
                storage.vm = controller.instance
                storage.save()
                instances.append(storage)

                item = {
                    'gb_quantity': storage.gb,
                    'gb_sku': storage_type_sku,
                    'storage_name': storage.name,
                    'storage_id': storage.pk,
                }
                storage_history.append(item)

            controller.instance.storages.set(instances)

        with tracer.start_span('generate_vm_history', child_of=span):
            history = models.VMHistory.objects.create(
                modified_by=self.request.user.id,
                customer_address=self.request.user.address['id'],
                project_id=controller.instance.project.pk,
                project_vm_name=f'{controller.instance.project.name}_{controller.instance.name}',
                state=state.REQUESTED,
                vm=controller.instance,
                **controller.vm_history,
            )

        with tracer.start_span('generate_storage_history', child_of=span):
            for line in storage_history:
                models.StorageHistory.objects.create(
                    vm_history=history,
                    **line,
                )

        controller.instance.refresh_from_db()
        return controller.instance

    def _create_vpn(self, data: Dict[str, Any], span: Span) -> models.VPN:
        """
        Create a VPN using the Controller and the supplied data.
        This has been put into its own method so that the update controller can also use it.

        # We need to add the ids to the data
        """
        tracer = settings.TRACER

        data['virtual_router_id'] = cast(models.VirtualRouter, self.virtual_router).id

        with tracer.start_span('validating_vpn_create_controller', child_of=self.request.span) as span:
            controller = VPNCreateController(
                request=self.request,
                data=data,
                span=span,
            )
            if not controller.is_valid():
                raise CloudCreateException(controller.errors)

        routes = controller.cleaned_data.pop('routes')
        vpn_clients = controller.cleaned_data.pop('vpn_clients', [])

        with tracer.start_span('get_stif_number', child_of=self.request.span):
            try:
                stif_number = get_stif_number(
                    self.request,
                    controller.instance.virtual_router.router,
                    'iaas_cloud_create_111',
                )
            except IAASException as e:  # pragma: no cover
                raise VPNCreateException(e.args[0])

        # Just save the instance and return it
        with tracer.start_span('set_vpn_details', child_of=span):
            controller.instance.stif_number = stif_number
            controller.instance.send_email = True
            controller.instance.save()

        num_clients = 0
        vpn_sku = skus.SITE_TO_SITE
        if vpn_clients:
            vpn_sku = skus.DYNAMIC_SECURE_CONNECT

        with tracer.start_span('saving_vpn_clients', child_of=span):
            for vpn_client in vpn_clients:
                vpn_client.vpn = controller.instance
                vpn_client.save()
                num_clients += 1

        with tracer.start_span('saving_routes', child_of=span):
            for route in routes:
                route.vpn = controller.instance
                route.save()

        # Generate VPN History
        with tracer.start_span('generate_vpn_history', child_of=span):
            models.VPNHistory.objects.create(
                modified_by=self.request.user.id,
                customer_address=controller.instance.virtual_router.project.address_id,
                project_id=controller.instance.virtual_router.project.pk,
                project_name=controller.instance.virtual_router.project.name,
                vpn=controller.instance,
                vpn_quantity=max(num_clients, 1),
                vpn_sku=vpn_sku,
            )

        return controller.instance

    def _create_firewall_rule(self, data: Dict[str, Any], order: int, span: Span) -> models.FirewallRule:
        """
        Create a FirewallRule using the Controller and the supplied data.
        This has been put into its own method so that the update controller can also use it.
        """
        controller = FirewallRuleCreateController(
            request=self.request,
            data=data,
            span=span,
            virtual_router=cast(models.VirtualRouter, self.virtual_router),
            order=order,
        )
        if not controller.is_valid():
            raise CloudCreateException(controller.errors)

        # Just save the instance and return it
        controller.instance.save()
        return controller.instance
