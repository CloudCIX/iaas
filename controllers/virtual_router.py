# stdlib
from collections import deque
from typing import Any, Deque, Dict, List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from . import helpers
from .subnet import SubnetCreateController, SubnetUpdateController
import iaas.state as states
from iaas.models import (
    ASN,
    IPAddress,
    Project,
    Route,
    Router,
    Subnet,
    VirtualRouter,
    VPN,
)

__all__ = [
    'VirtualRouterCreateController',
    'VirtualRouterListController',
    'VirtualRouterUpdateController',
]


class VirtualRouterListController(ControllerBase):
    """
    Lists the VirtualRouters.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase meta to make it more specific
        to the VirtualRouter list.
        """
        allowed_ordering = (
            'project__name',
            'created',
            'project__address_id',
            'project_id',
            'project__region_id',
            'state',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'ip_address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class VirtualRouterCreateController(ControllerBase):
    """
    Validates data used to create a VirtualRouter
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        model = VirtualRouter
        validation_order = (
            'project_id',
            'router',
            'ip_address',
        )

    def validate_project_id(self, project_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Project that the Virtual Router is associated with.
        type: integer
        """

        if project_id is None:
            return 'iaas_virtual_router_create_101'

        # Check if value is valid type.
        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            return 'iaas_virtual_router_create_102'

        # Check if project ID corresponds to valid project.
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return 'iaas_virtual_router_create_103'

        # Check if project already has a virtual router.
        if VirtualRouter.objects.filter(project=project).exists():
            return 'iaas_virtual_router_create_104'

        self.cleaned_data['project'] = project
        return None

    def validate_router(self, router: Optional[int]) -> Optional[str]:
        """
        description: Find the best fit Router in the chosen region to put the Virtual Router onto.
        type: integer
        generative: true
        """

        if 'project' not in self.cleaned_data:
            return None

        # Get routers in region
        region = self.cleaned_data['project'].region_id

        # Check if there is a Phantom Router with capacity of None for the Region
        phantom_router = Router.objects.filter(capacity__isnull=True, region_id=region)
        if phantom_router.exists():
            phantom = phantom_router.first()
            router_ip_addresses = phantom.router_ips
            if router_ip_addresses.count() == 0:
                return 'iaas_virtual_router_create_105'
            self.cleaned_data['router'] = phantom_router.first()
            self.cleaned_data['router_ip_addresses'] = router_ip_addresses
            return None

        # No phantom router, check if there is a Router with capacity available
        routers = Router.objects.filter(
            region_id=region,
            enabled=True,
        )
        if not routers.exists():
            return 'iaas_virtual_router_create_106'

        selected_router = None
        capacity_remaining = 0

        for router in routers:
            if router.capacity_available > capacity_remaining:  # type: ignore
                selected_router = router
                capacity_remaining = router.capacity_available  # type: ignore

        if capacity_remaining < 1:
            return 'iaas_virtual_router_create_107'

        router_ip_addresses = selected_router.router_ips  # type: ignore

        if router_ip_addresses.count() == 0:
            return 'iaas_virtual_router_create_108'

        self.cleaned_data['router'] = selected_router
        self.cleaned_data['router_ip_addresses'] = router_ip_addresses
        return None

    def validate_ip_address(self, ip_address: Optional[int]) -> Optional[str]:
        """
        description: Creates an IP Address for the Virtual Router and adds it to the instance.
        type: integer
        generative: true
        """

        if 'router' not in self.cleaned_data:
            return None

        region_subnets = [ip.subnet for ip in self.cleaned_data['router_ip_addresses'].all()]

        try:
            data = helpers.get_free_ip_in_router(
                region_subnets,
                'iaas_virtual_router_create_109',
                self.span,
            )
        except helpers.IAASException as e:  # pragma: no cover
            return e.args[0]
        ip = IPAddress.objects.create(
            address=data['address'],
            name=data['name'],
            subnet_id=data['subnet_id'],
        )

        self.cleaned_data['ip_address'] = ip
        return None


class VirtualRouterUpdateController(ControllerBase):
    """
    Validates data used to update a VirtualRouter
    """
    _instance: VirtualRouter
    update_virtual_router = False
    close_virtual_router = False
    scrub_virtual_router = False

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        model = VirtualRouter
        validation_order = (
            'state',
            'subnets',
        )

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        Extra handling of the errors property for handling the subnet errors in the case its a list
        """
        popped = False
        subnet_errors = self._errors.get('subnets', None)
        if isinstance(subnet_errors, list):
            # Remove it, call super and add it back in
            subnet_errors = self._errors.pop('subnets')
            popped = True
        errors = super(VirtualRouterUpdateController, self).errors
        if popped:
            errors['subnets'] = subnet_errors
        return errors

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: |
            Change the state of the Virtual Router, causing the CloudCIX Robot to perform requested actions on it.

            There is a specific set of states from which the user can request a change, and each of these allowed states
            has a subset of states it can be changed to. These are as follows;

            - RUNNING (4)     -> QUIESCE (5), or UPDATE (10)
            - QUIESCED (6)    -> RESTART (7), SCRUB (8) , or UPDATE (10)
            - SCRUB_QUEUE (9) -> QUIESCED (6), or RESTART (7)
        type: integer
        """
        if state is None:
            return None

        # Ensure sent value is of correct type.
        try:
            state = int(state)
        except (TypeError, ValueError):
            return 'iaas_virtual_router_update_101'

        # Check if current state is same as sent state.
        if self._instance.state == state:
            return None

        # Ensure state is in correct range.
        if state not in states.VALID_RANGE:
            return 'iaas_virtual_router_update_102'

        # Determine which state changes are available.
        if self.request.user.robot:
            available_states = states.ROBOT_STATE_MAP
        else:
            available_states = states.USER_STATE_MAP

        # Ensure current state is in chosen map.
        if self._instance.state not in available_states:
            return 'iaas_virtual_router_update_103'

        # Ensure sent state is a valid state change.
        if state not in available_states[self._instance.state]:
            return 'iaas_virtual_router_update_104'

        if state == states.SCRUBBING:
            self.scrub_virtual_router = True

        if state == states.CLOSED:
            self.close_virtual_router = True

        self.cleaned_data['state'] = state
        return None

    def validate_subnets(self, subnets: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            Validate list of Subnet dictionaries to be configured on the Virtual Router format of:
            'subnets':[{'address_range': '1.1.1.1/24', 'name': 'subnet name'}].
        type: List[Dict[str, Any]]
        """
        subnets = subnets or []

        if not isinstance(subnets, list):
            return 'iaas_virtual_router_update_105'

        if len(subnets) == 0:
            return 'iaas_virtual_router_update_106'

        # Get ASN for region
        try:
            asn = ASN.objects.get(number=(self._instance.project_id + ASN.pseudo_asn_offset))
        except ASN.DoesNotExist:
            return 'iaas_virtual_router_update_107'

        subnet_networks: List[Any] = []
        # Create each of the subnet instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(subnets))]
        instances: Deque[Subnet] = deque()

        for index, subnet in enumerate(subnets):

            # For all variations, we need to first validate the subnet using netaddr
            try:
                network = netaddr.IPNetwork(subnet['address_range'])
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_virtual_router_update_108'
            # Remember the new string value of the network
            address_range = str(network)

            # Firstly, check that the chosen gateway is not one of the restricted addresses
            if network.ip in {network.network, network.broadcast}:
                return 'iaas_virtual_router_update_109'

            # Ensure none of the sent subnets overlap with each other
            for n in netaddr.IPSet(subnet_networks).iter_cidrs():
                if network in n or n in network:
                    return 'iaas_virtual_router_update_110'

            # Ensure none of the Routes/remote_subnets in this virtual router overlap with this subnet.
            # get vpns for this virtual router
            vpn_ids = VPN.objects.filter(
                deleted__isnull=True,
                virtual_router_id=self._instance.id,
            ).values_list('pk', flat=True)
            if any(vpn_ids):
                existing_remote_subnets = netaddr.IPSet(
                    Route.objects.filter(
                        deleted__isnull=True,
                        vpn_id__in=vpn_ids,
                    ).values_list('remote_subnet', flat=True),
                )
                for remote_subnet in existing_remote_subnets.iter_cidrs():
                    if network in remote_subnet or remote_subnet in network:
                        return 'iaas_virtual_router_update_111'

            pk = subnet.get('id', None)
            if pk is None:
                # Create
                # Determine which allocation the Subnet needs to go into
                found = False
                for allocation in asn.allocations.iterator():
                    if network not in netaddr.IPNetwork(allocation.address_range):
                        continue
                    subnet['allocation_id'] = allocation.pk
                    found = True
                    break
                if not found:
                    return 'iaas_virtual_router_update_112'

                subnet['address_id'] = self.request.user.address['id']
                subnet['address_range'] = address_range
                subnet['vxlan'] = self.request.user.address['id']
                controller = SubnetCreateController(data=subnet, request=self.request, span=self.span)

            else:
                # Update
                try:
                    instance = Subnet.objects.get(pk=pk)
                except Subnet.DoesNotExist:  # pragma: no cover
                    return 'iaas_virtual_router_update_113'
                controller = SubnetUpdateController(
                    data=subnet,
                    instance=instance,
                    request=self.request,
                    span=self.span,
                )

            # Validate the controller
            if not controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = controller.errors
                continue

            subnet_networks.append(address_range)
            # Add the instance to the instances deque
            instances.append(controller.instance)

        # Check if any subnet item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['subnets'] = errors
            return None

        # Update Virtual Router to configure subnets
        self.update_virtual_router = True

        self.cleaned_data['subnets'] = instances
        return None
