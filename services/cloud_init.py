# libs
from jaeger_client import Span
from rest_framework.request import Request
# local
from iaas.controllers.helpers import get_free_ip_in_router, IAASException, create_cloud_subnets
from iaas.models import (
    Allocation,
    ASN,
    IPAddress,
    Project,
    Subnet,
    VirtualRouter,
)

__all__ = [
    'METADATA_ADDRESS_RANGE',
    'METADATA_ALLOCATION_RANGE',
    'METADATA_VLANS',
    'RESERVED_METADATA_IP',
    'get_metadata_ip',
    'ensure_service_bus_exists',
]


RESERVED_METADATA_IP = '169.254.169.254'
METADATA_ALLOCATION_RANGE = '169.254.0.0/16'
METADATA_ADDRESS_RANGE = '169.254.0.1/16'
METADATA_VLANS = range(100, 1000)


def get_metadata_ip(request: Request, project: Project, vlan_error: str, ip_error: str, span: Span):
    # Get the subnet that metadata will be served through
    subnet = ensure_service_bus_exists(request, project, vlan_error, span)

    # Get an IP from this Subnet
    ip = get_free_ip_in_router([subnet], ip_error, span)

    return {
        'address': ip['address'],
        'subnet_id': ip['subnet_id'],
        'name': 'Metadata IP',
    }


def ensure_service_bus_exists(
        request: Request,
        project: Project,
        vlan_error: str,
        span: Span,
) -> Subnet:
    """
    Make sure that a Service Bus subnet (169.254.0.1/16) exists for the given Project
    :param request: The object representing the user's request
    :param project: The project that needs a Service Bus
    :param vlan_error: An error code to be thrown if no VLANs are available for the subnet
    :return: A 169.254.0.0/16 private subnet
    """
    subnet, created = Subnet.objects.get_or_create(
        address_id=project.address_id,
        address_range=METADATA_ADDRESS_RANGE,
        allocation=Allocation.objects.get(
            address_id=project.address_id,
            asn__number=ASN.pseudo_asn_offset + project.pk,
            address_range=METADATA_ALLOCATION_RANGE,
        ),
        cloud=True,
        name='service bus',
        virtual_router_id=VirtualRouter.objects.values_list('id', flat=True).get(project=project.pk),
    )
    if not created:
        return subnet

    # Get a VLAN for the Subnet
    try:
        subnet = create_cloud_subnets(request, project, [subnet], vlan_error, span, vlan_range=METADATA_VLANS)[0]
    except IAASException as e:
        subnet.delete()
        raise e

    # Reserve the IP for the Metadata Server and Gateway
    IPAddress.objects.create(
        address=RESERVED_METADATA_IP,
        cloud=True,
        name='Metadata Server',
        subnet=subnet,
    )
    IPAddress.objects.create(
        address=METADATA_ADDRESS_RANGE.split('/')[0],
        cloud=True,
        name='Metadata Gateway',
        subnet=subnet,
    )
    return subnet
