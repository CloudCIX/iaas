# stdlib
from collections import deque
from typing import Any, cast, Deque, Dict, List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from cloudcix_rest.utils import get_error_details
from django.conf import settings
from jaeger_client import Span
# local
from iaas import models, state
from iaas.utils import get_vm_interface_mac_address
from ..firewall_rule import FirewallRuleCreateController
from ..helpers import create_cloud_subnets, IAASException
from ..project import ProjectCreateController
from ..virtual_router import VirtualRouterUpdateController
from ..vm import VMCreateController


__all__ = [
    'CloudCreateController',
    'CloudCreateException',
]


class CloudCreateException(Exception):
    """For exceptions from the _create_* methods"""
    response: Dict[str, Any]

    def __init__(self, response: Dict[str, Any]) -> None:
        self.response = response


class CloudCreateController(ControllerBase):
    """
    Validates Cloud data used to create an entire Cloud Project safely.
    """

    # Instance variables of every cloud item
    firewall_rules: Deque[models.FirewallRule]
    project: Optional[models.Project] = None
    virtual_router: Optional[models.VirtualRouter] = None
    vms: Deque[models.VM]

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        validation_order = (
            'project',
            'subnets',
            'vms',
            'firewall_rules',
        )

    def __init__(self, *args, **kwargs) -> None:
        super(CloudCreateController, self).__init__(*args, **kwargs)
        self.firewall_rules = deque()
        self.vms = deque()

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        If the user requests errors, delete all the objects.

        Then, potentially check for modifications that need to be made to error fields.
        """
        # Delete objects
        for firewall in self.firewall_rules:
            firewall.delete()
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
        self.project.save()
        self.project.set_run_robot_flags()

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
            return 'iaas_cloud_create_107'

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
                code = 'iaas_cloud_create_108'
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
            # Only one IP from each subnet(interface) on a VM needs to assigned a mac_address
            mac_address_subnets: List = []
            region_id = controller.instance.project.region_id
            server_type_id = controller.instance.server.type.id
            for ip in ip_addresses:
                ip_address = models.IPAddress.objects.create(
                    vm=controller.instance,
                    modified_by=self.request.user.id,
                    **ip,
                )
                if ip['subnet'].pk not in mac_address_subnets:
                    ip_address.mac_address = get_vm_interface_mac_address(region_id, server_type_id, ip_address.pk)
                    ip_address.save()
                    mac_address_subnets.append(ip['subnet'].pk)

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
