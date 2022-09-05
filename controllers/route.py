# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from jaeger_client import Span
import netaddr
from rest_framework.request import QueryDict, Request
# local
from iaas.controllers.helpers import get_available_dynamic_remote_subnets, IAASException
from iaas.models import ASN, Route, Subnet, VirtualRouter, VPN


__all__ = [
    'RouteCreateController',
    'RouteUpdateController',
]


class RouteCreateController(ControllerBase):
    """
    Validates user data used to create a new route record
    """

    class Meta(ControllerBase.Meta):
        model = Route
        validation_order = (
            # 'virtual_router_id',
            'local_subnet',
            'remote_subnet',
        )

    def __init__(
            self,
            request: Request,
            data: QueryDict,
            span: Optional[Span],
            virtual_router: VirtualRouter,
            vpn_id: Optional[int],
            vpn_type: str,
    ) -> None:
        """
        Override the init to allow for adding extra fields from outside into the system.
        :param request: The request sent by the User
        :param data: The data being validated. Either request.GET or request.POST depending on the method
        :param span: A Span instance that is the parent span of the controller. Passing this in will allow us torecord
                     time taken to run the validation methods in the controller.
        :param virtual_router: The virtual router being used to configure Route for VPN on
        :param vpn_id: The ID of VPN the route is to be configured on. This is only required when adding a Route to an
                       existing VPN.
       :param vpn_type: The type of VPN the route is to be configured on.
        """
        super(RouteCreateController, self).__init__(request=request, data=data, span=span)
        self.cleaned_data['virtual_router'] = virtual_router
        self.cleaned_data['vpn_type'] = vpn_type
        if bool(vpn_id):
            self.cleaned_data['vpn_id'] = vpn_id

    def validate_local_subnet(self, local_subnet: Optional[int]) -> Optional[str]:
        """
        description: The local Subnet in VPN Tunnel's Project that will be configured as part of this Route
        type: integer
        """
        if local_subnet is None:
            return 'iaas_route_create_101'
        # Ensure the address id is valid
        try:
            local_subnet = netaddr.IPNetwork(local_subnet)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_route_create_102'

        try:
            subnet = Subnet.objects.get(
                deleted__isnull=True,
                address_range=str(local_subnet),
                allocation__asn__number=self.cleaned_data['virtual_router'].project.pk + ASN.pseudo_asn_offset,
            )
        except Subnet.DoesNotExist:
            return 'iaas_route_create_103'

        self.cleaned_data['local_subnet'] = subnet
        return None

    def validate_remote_subnet(self, remote_subnet: Optional[str]) -> Optional[str]:
        """
        description: |
            CIDR notation of the Remote Subnet on the Customer side of the VPN Tunnel that should be given access
            through the VPN.
            Please note that none of the sent address range can overlap with the subnets configured on this VPN's
            virtual router. Also the sent address range cannot overlap with a remote subnet of another VPN in the same
            Project.

        type: string
        """
        # Ensure a value was sent
        if remote_subnet is None:
            return 'iaas_route_create_104'
        # For all variations, we need to first validate the remote_subnet using netaddr
        try:
            network = netaddr.IPNetwork(remote_subnet)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_route_create_105'

        # Ensure remote subnet does not overlap with any of the subnets configured on requested VPN's virtual router if
        # remote is a Private Subnet
        if netaddr.IPNetwork(remote_subnet).is_private():
            vr_subnets = netaddr.IPSet(Subnet.objects.filter(
                deleted__isnull=True,
                virtual_router_id=self.cleaned_data['virtual_router'].pk,
            ).values_list('address_range', flat=True))
            for subnet in vr_subnets.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_route_create_106'

        # If there are other VPNs in same project, ensure this remote subnet does not overlap with their remote subnets.
        vpn_ids = VPN.objects.filter(
            deleted__isnull=True,
            virtual_router_id=self.cleaned_data['virtual_router'].pk,
        ).values_list('pk', flat=True)
        if 'vpn_id' in self.cleaned_data:
            vpn_ids = vpn_ids.exclude(pk=self.cleaned_data['vpn_id'])
        if bool(vpn_ids):
            existing_remote_subnets = netaddr.IPSet(
                Route.objects.filter(
                    deleted__isnull=True,
                    vpn_id__in=vpn_ids,
                ).values_list('remote_subnet', flat=True),
            )
            for subnet in existing_remote_subnets.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_route_create_107'

        if self.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            # Ensure remote subnet is  a /24 in 172.16.0.0/12
            if network not in Route.DYNAMIC_REMOTE_SUBNET_NETWORKS:
                return 'iaas_route_create_108'

            # Get available dynamic subnets for vpn's virtual router's project's region
            try:
                available = get_available_dynamic_remote_subnets(
                    request=self.request,
                    region_id=self.cleaned_data['virtual_router'].project.region_id,
                    dynanmic_remote_subnet_error='iaas_route_create_109',
                )
            except IAASException as e:
                return e.args[0]

            # Ensure subnet is in the available list
            if str(network.cidr) not in available:
                return 'iaas_route_create_110'

        self.cleaned_data['remote_subnet'] = network.cidr
        return None


class RouteUpdateController(ControllerBase):
    """
    Validates user data used to update existing Route record
    """

    class Meta(ControllerBase.Meta):
        model = Route
        validation_order = (
            'local_subnet',
            'remote_subnet',
        )

    def validate_local_subnet(self, local_subnet: Optional[int]) -> Optional[str]:
        """
        description: The local Subnet in VPN Tunnel's Project that will be configured as part of this Route
        type: integer
        """
        if local_subnet is None:
            return 'iaas_route_update_101'
        # Ensure the address id is valid
        try:
            local_subnet = netaddr.IPNetwork(local_subnet)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_route_update_102'

        try:
            subnet = Subnet.objects.get(
                deleted__isnull=True,
                address_range=str(local_subnet),
                allocation__asn__number=self._instance.vpn.virtual_router.project.pk + ASN.pseudo_asn_offset,
            )
        except Subnet.DoesNotExist:
            return 'iaas_route_update_103'

        self.cleaned_data['local_subnet'] = subnet
        return None

    def validate_remote_subnet(self, remote_subnet: Optional[str]) -> Optional[str]:
        """
        description: |
            CIDR notation of the Remote Subnet on the Customer side of the VPN Tunnel that should be given access
            through the VPN.
            Please note that none of the sent address range can overlap with the subnets configured on this VPN's
            virtual router. Also the sent address range cannot overlap with a remote subnet of another VPN in the same
            Project.

        type: string
        """
        # Ensure a value was sent
        if remote_subnet is None:
            return 'iaas_route_update_104'
        # For all variations, we need to first validate the remote_subnet using netaddr
        try:
            network = netaddr.IPNetwork(remote_subnet)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_route_update_105'

        # Ensure remote subnet does not overlap with any of the subnets configured on requested VPN's virtual router.
        if netaddr.IPNetwork(remote_subnet).is_private():
            vr_subnets = netaddr.IPSet(Subnet.objects.filter(
                deleted__isnull=True,
                virtual_router_id=self._instance.vpn.virtual_router.pk,
            ).values_list('address_range', flat=True))
            for subnet in vr_subnets.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_route_update_106'

        # If there are other VPNs in same project, ensure this remote subnet does not overlap with their remote subnets.
        vpn_ids = VPN.objects.filter(
            deleted__isnull=True,
            virtual_router_id=self._instance.vpn.virtual_router.pk,
        ).exclude(
            pk=self._instance.vpn.pk,
        ).values_list('pk', flat=True)

        if bool(vpn_ids):
            existing_remote_subnets = netaddr.IPSet(
                Route.objects.filter(
                    deleted__isnull=True,
                    vpn_id__in=vpn_ids,
                ).values_list('remote_subnet', flat=True),
            )

            for subnet in existing_remote_subnets.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_route_update_107'

        if self._instance.vpn.vpn_type == VPN.DYNAMIC_SECURE_CONNECT and \
                str(network.cidr) != self._instance.remote_subnet:

            # Ensure remote subnet is  a /24 in 172.16.0.0/12
            if network not in Route.DYNAMIC_REMOTE_SUBNET_NETWORKS:
                return 'iaas_route_update_108'

            # Get available dynamic subnets for vpn's virtual router's project's region
            try:
                available = get_available_dynamic_remote_subnets(
                    request=self.request,
                    region_id=self._instance.vpn.virtual_router.project.region_id,
                    dynanmic_remote_subnet_error='iaas_route_update_109',
                )
            except IAASException as e:
                return e.args[0]

            # Ensure subnet is in the available list
            if str(network.cidr) not in available:
                return 'iaas_route_update_110'

        self.cleaned_data['remote_subnet'] = network.cidr
        return None
