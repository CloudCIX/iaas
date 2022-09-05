"""
Helper functions
"""
# python
import logging
from random import choice
from typing import Any, Dict, List, Optional, Union
# libs
from django.conf import settings
import netaddr
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas import state
from iaas.models import (
    ASN,
    IPAddress,
    Project,
    Subnet,
    Route,
    Router,
    VPN,
)

if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
    VLAN_RANGE = range(1000, 2001)
else:
    # Alpha can currently only use 1000 - 1099
    VLAN_RANGE = range(1000, 1100)


class IAASException(Exception):
    pass


def create_public_ip(request: Request, region_subnet: Subnet, ip_error: str, span: Span) -> IPAddress:
    """
    Helper method that will generate a public IP address for a given private cloud IPAddress.
    """
    return IPAddress.objects.create(
        modified_by=request.user.id,
        **get_free_ip_in_router([region_subnet], ip_error, span),
    )


def get_free_ip_in_router(region_subnets: List[Subnet], ip_error: str, span: Span) -> Dict[str, Any]:
    """
    Given a list of IP Addresses that are on the project's router, generate a free public IP address from the same
    range and return a dictionary of data required to create it
    """
    logger = logging.getLogger('iaas.controllers.helpers.get_free_ip_in_router')

    # Get the networks associated with the regions subnets
    networks = [netaddr.IPNetwork(subnet.address_range) for subnet in region_subnets]

    # Find all the existing Cloud IPs in use in those Subnets in question
    existing = {
        netaddr.IPAddress(addr)
        for addr in IPAddress.objects.filter(subnet__in=region_subnets).values_list('address', flat=True).iterator()
    }
    # Subtract 2 from each size to not include network and broadcast addresses
    total_possible = sum(network.size - 2 for network in networks)
    if len(existing) == total_possible:  # pragma: no cover
        logger.error(
            f'No available Floating IP Addresses from the subnet of the following subnets: {region_subnets}',
        )
        raise IAASException(ip_error)

    # Find a free Address in the Subnets that were returned (double randomness to avoid race conditions)
    found = False
    # We know that we have to find one if we look hard enough because we're not full
    while not found:
        network = choice(networks)
        ip = choice(network)
        if ip in existing or ip in {network.network, network.broadcast}:  # pragma: no cover
            continue
        found = True

    subnet = [sub for sub in region_subnets if sub.address_range == str(network)]
    return {
        'address': str(ip),
        'cloud': True,
        'subnet_id': subnet[0].pk,
        'name': 'Floating IP',
    }


def create_cloud_subnets(
    request: Request,
    project: Project,
    subnets: List[Subnet],
    vlan_error: str,
    span: Span,
    vlan_range: range = VLAN_RANGE,
) -> Union[List[int], str]:
    """
    Given a list of subnets and the project they are to be configures on, find a free VLAN for each subnet in the
    project's region and save the subnet.
    """
    logger = logging.getLogger('iaas.controllers.helpers.create_cloud_subnets')

    project_ids = Project.objects.filter(region_id=project.region_id).values_list('pk', flat=True)
    existing = set(Subnet.objects.filter(
        allocation__asn__number__in=[(id + ASN.pseudo_asn_offset) for id in project_ids],
        cloud=True,
        vlan__gte=vlan_range[0],
        vlan__lte=vlan_range[-1],
    ).distinct().values_list('vlan', flat=True))

    if len(existing) + len(subnets) >= len(vlan_range):
        logger.error(
            'Error occurred when attempting to create cloud subnets. No VLANS available in region '
            f'#{project.region_id}',
        )
        raise IAASException(vlan_error)

    free = [v for v in vlan_range if v not in existing]

    index = 0
    for subnet in subnets:
        # Find a vlan for this Subnet from the available vlans in this region.
        subnet.vlan = free[index]
        subnet.cloud = True
        subnet.modified_by = request.user.id
        subnet.virtual_router_id = project.virtual_router.pk
        subnet.save()

        index += 1

    return subnets


def get_stif_number(request: Request, router: Router, stif_number_error: str) -> Optional[str]:
    """
    Helper method to find an available stif number on a Router for a VPN
    """
    logger = logging.getLogger('iaas.controllers.helpers.get_stif_number')

    existing = set(VPN.objects.filter(
        stif_number__gte=VPN.STIF_NUMBER_RANGE[0],
        stif_number__lte=VPN.STIF_NUMBER_RANGE[-1],
        virtual_router__router=router,
    ).distinct().values_list('stif_number', flat=True))

    if len(existing) >= len(VPN.STIF_NUMBER_RANGE):
        logger.error(
            f'Error occurred when attempting to create VPN. No stif numbers available in region #{router.region_id}',
        )
        raise IAASException(stif_number_error)

    stif_number = choice(VPN.STIF_NUMBER_RANGE)
    while stif_number in existing:  # pragma: no cover
        stif_number = choice(VPN.STIF_NUMBER_RANGE)

    return stif_number


def get_available_dynamic_remote_subnets(
    request: Request,
    region_id: int,
    dynanmic_remote_subnet_error: str,
    search_value: Optional[str] = None,
) -> Optional[List[str]]:
    """
    Helper method to find available dynamic subnets in a region
    """
    logger = logging.getLogger('iaas.controllers.helpers.get_available_dynamic_remote_subnets')

    existing = list(Route.objects.filter(
        vpn__virtual_router__project__region_id=region_id,
        vpn__vpn_type=VPN.DYNAMIC_SECURE_CONNECT,
        deleted__isnull=True,
    ).exclude(
        vpn__virtual_router__state=state.CLOSED,
    ).values_list('remote_subnet', flat=True).iterator())

    if bool(search_value):
        dynamic_remote_subnets = [
            a for a in Route.DYNAMIC_REMOTE_SUBNET_LIST if (a not in existing and search_value in a)
        ]
    else:
        dynamic_remote_subnets = [a for a in Route.DYNAMIC_REMOTE_SUBNET_LIST if a not in existing]

    if len(dynamic_remote_subnets) == 0:
        logger.error(f'No available Dynamic Remote Subnets in region #{region_id}.')
        raise IAASException(dynanmic_remote_subnet_error)

    return dynamic_remote_subnets
