# stdlib
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple
# libs
from cloudcix_rest.controllers import ControllerBase
from cloudcix_rest.utils import get_error_details
from django.conf import settings
from jaeger_client import Span
from rest_framework.request import QueryDict, Request
# local
from iaas import models, state, skus
from .create import CloudCreateController, CloudCreateException
from ..helpers import create_cloud_subnets, IAASException
from ..project import ProjectUpdateController
from ..virtual_router import VirtualRouterUpdateController
from ..vm import VMUpdateController


__all__ = [
    'CloudUpdateController',
]


class CloudUpdateException(CloudCreateException):
    """For exceptions from the _update_* methods"""


class CloudUpdateController(CloudCreateController):
    """
    Validates Cloud data used to update an entire Cloud Project safely.

    This includes creating new objects where necessary
    """
    project: models.Project
    virtual_router: models.VirtualRouter

    # Need to save some things for create / update
    _current_fw_rules: List[models.FirewallRule] = []
    _current_subnets: List[models.Subnet] = []
    _current_vm_devices: List[models.Device] = []
    _current_vm_ips: List[models.IPAddress] = []
    _new_fw_rules: Deque[models.FirewallRule]
    _new_storages: Deque[models.Storage]
    _new_vms: Deque[models.VM]
    _new_vm_devices: List[models.Device] = []
    _new_vm_ips: Deque[models.IPAddress]
    _router_initial_state: int = -1
    _update_storages: Deque[models.Storage]
    _update_histories: Deque[models.VMHistory]
    _update_virtual_router: bool = False
    _run_robot: bool = False
    subnet_ids: List[int] = []

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

    def __init__(
            self,
            request: Request,
            data: QueryDict,
            span: Optional[Span],
            project: models.Project,
            virtual_router: models.VirtualRouter,
    ) -> None:
        """
        Override the init to allow for adding extra fields from outside into the system.
        """

        super(CloudUpdateController, self).__init__(request=request, data=data, span=span)
        self.project = project
        self.virtual_router = virtual_router

        # Extra stuff
        self._new_fw_rules = deque()
        self._new_storages = deque()
        self._new_vms = deque()
        self._new_vm_devices: List[Any] = []
        self._new_vm_ips = deque()
        self._update_storages = deque()
        self._update_histories = deque()

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        If the user request has errors, reset the state of the project back to where it was before the request was made.

        Then, potentially check for modifications that need to be made to error fields.
        """
        # Delete the new FW rules (if any)
        for fw in self._new_fw_rules:
            fw.delete()

        # Delete any new storage objects
        for storage in self._new_storages:
            storage.delete()

        # Delete the new ips created
        for ip in self._new_vm_ips:  # pragma: no cover
            ip.cascade_delete()

        # Save back the old ips
        for ip in self._current_vm_ips:
            ip.save()
            if ip.public_ip is not None:
                ip.public_ip.deleted = None
                ip.public_ip.save()

        # Remove vm_id from the all devices for vm
        for device in self._new_vm_devices:
            device.vm_id = None
            device.save()

        # Save back the old devices with vm_id
        for device in self._current_vm_devices:
            device.save()

        # Delete new VMs
        for vm in self._new_vms:    # pragma: no cover
            vm.delete()

        # Delete new subnets:
        models.Subnet.objects.filter(virtual_router_id=self.virtual_router.pk).exclude(pk__in=self.subnet_ids).delete()

        # Save back the old subnets:
        for subnet in self._current_subnets:
            subnet.save()

        # Handle any necessary modifications to the errors dict that needs to be made
        errors = {}
        for field, error in self._errors.items():
            if isinstance(error, str):
                error = get_error_details(error)[error]
            errors[field] = error
        return errors

    def save(self):
        """
        If this method is called, go through the objects that have states and update them as necessary;
            - Set new objects to state 1
            - Set updated objects to state 10
            - Don't touch non-updated objects
        """
        # Delete the old firewall rules to allow the new ones to replace them
        for fw in self._current_fw_rules:
            fw.delete()

        # Save new and updated VMs and histories
        for history in self._update_histories:
            history.save()
        for vm in self._new_vms:
            vm.state = state.REQUESTED
            vm.save()
        for vm in self.vms:
            vm.save()

        for storage in self._update_storages:
            storage.save()

        # Check if we need to update the VirtualRouter
        if self._update_virtual_router:
            update_state = state.RUNNING_UPDATE
            if self.virtual_router.state == state.QUIESCED:
                update_state = state.QUIESCED_UPDATE
            self.virtual_router.state = update_state

        self.virtual_router.save()
        self.project.save()

        if self._run_robot or self._update_virtual_router:
            self.project.set_run_robot_flags()

    def validate_project(self, project: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        $ref: '#/components/schemas/ProjectUpdate'
        """
        if project is None:
            return 'iaas_cloud_update_101'

        if not isinstance(project, dict):
            return 'iaas_cloud_update_102'

        # Pass the sent data into the Project Controller
        controller = ProjectUpdateController(
            request=self.request,
            data=project,
            instance=self.project,
            span=self.span,
        )
        if not controller.is_valid():
            self._errors['project'] = controller.errors
            return None

        # Don't call save on Project to allow rollback
        self.project = controller.instance
        return None

    def validate_subnets(self, subnets: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects containing details of the Subnets to be created or updated in the Virtual Router for
            this Project.

            To update existing Subnets, include the `id` field.
            Without this field, the API will create a new Subnet using the sent details.
        type: array
        items:
            type: object
            properties:
                id:
                    description: |
                        The ID of the Subnet to be updated.

                        The presence or absence of this field denotes whether the API should update an existing Subnet
                        or create a new one respectively.
                    type: integer
                address_range:
                    description: |
                        The CIDR notation for the address range of the Subnet.

                        The sent address will be used as the gateway, so this value can not match the network or
                        broadcast addresses. For example; 10.0.0.1/24 is okay but 10.0.0.0/24 is not.

                        The address_range is only for new Subnets, update will ignore this value.
                    type: string
                name:
                    description: A verbose name used to identify the Subnet
                    type: string
            required:
                - name
        """
        subnets = subnets or []
        data = {'subnets': subnets}

        # Get current subnets
        self._current_subnets = models.Subnet.objects.filter(virtual_router_id=self.virtual_router.pk)
        self.subnet_ids = [sub.pk for sub in self._current_subnets]

        controller = VirtualRouterUpdateController(
            request=self.request,
            data=data,
            span=self.span,
            instance=self.virtual_router,
        )
        if not controller.is_valid():
            self._errors['virtual_router'] = controller.errors
            return None

        # Save the subnets temporarily as well
        subs = controller.cleaned_data.pop('subnets', {})

        new_subs: List[models.Subnet] = []
        for sub in subs:
            if not sub.pk:
                new_subs.append(sub)
            else:
                sub.save()

        if len(new_subs) > 0:
            try:
                create_cloud_subnets(
                    self.request,
                    self.project,
                    new_subs,
                    'iaas_cloud_update_103',
                    span=self.span,
                )
            except IAASException as e:  # pragma: no cover
                self._errors['subnets'] = e.args[0]
                return None

        if controller.update_virtual_router and controller.instance.can_update():
            self._update_virtual_router = True

        # We add the subnets to self.subnets immediately after creation because we need to know what to delete in case
        # of errors, so we don't have to do anything here
        return None

    def validate_vms(self, vms: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of objects containing details of the VMs to be created or updated in the Project.

            To update existing VMs, include the `id` field.
            Without this field, the API will create a new VM using the sent details.
        type: array
        items:
            type: object
            required:
                - image_id
                - storage_type_id
                - storages
                - cpu
                - gpu
                - ram
                - dns
                - name
                - gateway_subnet
                - ip_addresses
            properties:
                id:
                    description: |
                        The ID of the VM to be updated.

                        The presence or absence of this field denotes whether the API should update an existing VM
                        or create a new one respectively.
                    type: integer
                image_id:
                    description: The ID of the Image that will be used to build the VM.
                    type: integer
                nat:
                    description: |
                        A flag stating whether or not the VM should have a public IP Address created for it.

                        Optional, defaults to False.
                    type: boolean
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
                gpu:
                    description: |
                        The number of GPUSs that the VM should be updated with.
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
        vms = vms or []
        if not isinstance(vms, list):
            return 'iaas_cloud_update_104'
        if len(vms) == 0:
            return 'iaas_cloud_update_105'

        tracer = settings.TRACER

        # Set up a list of errors
        errors: List[Optional[Dict[str, Any]]] = [None for _ in vms]

        # Iterate through the list and attempt to create each VM in question
        for index, data in enumerate(vms):
            if not isinstance(data, dict):
                code = 'iaas_cloud_update_106'
                errors[index] = get_error_details(code)[code]
                continue

            pk = data.get('id', None)
            # New VM
            if pk is None:
                try:
                    with tracer.start_span(f'_create_vm_{index}', child_of=self.span) as span:
                        vm = self._create_vm(data, span)
                        self._new_vms.append(vm)
                        self._run_robot = True
                except CloudCreateException as e:
                    errors[index] = e.response

            else:
                with tracer.start_span(f'_update_vm_{index}', child_of=self.span) as span:
                    try:
                        vm, history = self._update_vm(pk, data, span)
                        self.vms.append(vm)
                        if history is not None:
                            self._update_histories.append(history)
                    except CloudUpdateException as e:
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
            return 'iaas_cloud_update_107'

        # Save the old firewall rules to delete if we are successful
        self._current_fw_rules = list(self.virtual_router.firewall_rules.iterator())

        # Early out, if list is empty,_current_fw_rules will be deleted on save()
        if len(firewall_rules) == 0:
            if any(self._current_fw_rules) and self.virtual_router.can_update():
                self._update_virtual_router = True
            return None

        tracer = settings.TRACER

        # Set up a list of errors
        errors: List[Optional[Dict[str, Any]]] = [None for _ in firewall_rules]

        # Iterate through the list and attempt to create each FR in question
        for index, data in enumerate(firewall_rules):
            if not isinstance(data, dict):
                code = 'iaas_cloud_update_108'
                errors[index] = get_error_details(code)[code]
                continue

            try:
                with tracer.start_span(f'_create_firewall_rule_{index}', child_of=self.span) as span:
                    self._new_fw_rules.append(self._create_firewall_rule(data, index, span))
            except CloudCreateException as e:
                errors[index] = e.response

        # Check if we have errors to report
        if any(error is not None for error in errors):
            self._errors['firewall_rules'] = errors

        # Refresh the virtual router again to access the Firewall Rules
        self.virtual_router.refresh_from_db()
        if self.virtual_router.can_update():
            self._update_virtual_router = True

        # We add the firewall_rules to self._new_fw_rules immediately after creation because we need to know what to
        # delete in case of errors, so we don't have to do anything here
        return None

    def _update_vm(self, pk: int, data: Dict[str, Any], span: Span) -> Tuple[models.VM, Optional[models.VMHistory]]:
        """
        Update the VM with the specified pk (if it exists).

        Returns a tuple that contains the VM and a flag stating whether or not the state should be changed to 10
        before saving.
        The returned VM instance will have updated data but will need to be saved
        """
        tracer = settings.TRACER
        with tracer.start_span('fetching_object', child_of=span):
            try:
                obj = models.VM.objects.get(pk=pk, project=self.project)
            except models.VM.DoesNotExist:
                code = 'iaas_cloud_update_109'
                raise CloudUpdateException(get_error_details(code)[code])

        # Save the old vm ips to save back if we are unsuccessful
        for ip in obj.vm_ips.all():
            self._current_vm_ips.append(models.IPAddress.objects.get(pk=ip.pk))

        # Save the old vm devices to save back if we are unsuccessful
        current_devices = models.Device.objects.filter(vm_id=pk)
        for device in current_devices:
            self._current_vm_devices.append(device)

        # Make sure they don't mess with state through this
        data['state'] = obj.state

        with tracer.start_span('validating_controller', child_of=span) as child_span:
            controller = VMUpdateController(
                request=self.request,
                data=data,
                span=child_span,
                instance=obj,
            )
            if not controller.is_valid():
                raise CloudUpdateException(controller.errors)

        history = None
        with tracer.start_span('generate_vm_history', child_of=span) as child_span:
            if controller.create_vm_history:
                history = models.VMHistory.objects.create(
                    modified_by=self.request.user.id,
                    customer_address=obj.project.address_id,
                    project_id=obj.project.pk,
                    project_vm_name=f'{obj.project.name}_{controller.instance.name}',
                    vm=controller.instance,
                    **controller.vm_history,
                )
                with tracer.start_span('saving_storages_and_history', child_of=child_span):
                    # Create storage histories, which will all delete properly if the above is deleted
                    storages_to_update = controller.cleaned_data.pop('storages_to_update', [])
                    for storage in controller.cleaned_data.get('storages', []):
                        create_storage_history = False
                        # If storage is new, save it now for an id to be created
                        if storage.pk is None:
                            # Save it and append to the deque
                            storage.vm_id = obj.pk
                            storage.save()
                            self._new_storages.append(storage)
                            create_storage_history = True
                        else:
                            self._update_storages.append(storage)
                            if storage.pk in storages_to_update:
                                create_storage_history = True
                        if create_storage_history:
                            sku = skus.STORAGE_SKU_MAP[obj.server.storage_type_id]
                            models.StorageHistory.objects.create(
                                vm_history=history,
                                gb_quantity=storage.gb,
                                gb_sku=sku,
                                storage_name=storage.name,
                                storage_id=storage.pk,
                            )

        self.virtual_router.refresh_from_db()
        if controller.update_virtual_router and self.virtual_router.can_update():  # pragma: no cover
            self._update_virtual_router = True

        # Save the new vm devices to delete if we are unsuccessful (controller adds vm_id to Device to reduce chance
        # of race conditions)
        current_devices = models.Device.objects.filter(vm_id=pk)
        for device in current_devices:
            self._new_vm_devices.append(device)

        return controller.instance, history
