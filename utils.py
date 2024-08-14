# stdlib
from math import sqrt
from typing import Dict, List
# libs
from cloudcix.api.membership import Membership
import netaddr
# local


__all__ = [
    'get_addresses_in_member',
    'get_region_cache_key',
]


def get_addresses_in_member(request, span) -> Dict[int, str]:
    """
    Given a token, make requests to Membership to fetch all the Addresses in the Member that the token is from
    """
    params = {
        'page': 0,
        'limit': 50,
        'search[member_id]': request.user.member['id'],
    }
    response = Membership.address.list(
        token=request.user.token,
        params=params,
        span=span,
    )
    address_ids = {a['id']: a['name'] for a in response.json()['content']}

    total_records = response.json()['_metadata']['total_records']
    while len(address_ids) < total_records:  # pragma: no cover
        params['page'] += 1
        response = Membership.address.list(
            token=request.user.token,
            params=params,
            span=span,
        )
        for a in response.json()['content']:
            address_ids[a['id']] = a['name']

    return address_ids


def magnitude(vec: List[int]) -> float:
    """
    Calculate the magnitude (length) of a vector
    :param vec: A vector, represented by a sequence of integers
    :return: The magnitude of vec
    """
    return sqrt(sum({val * val for val in vec}))


def dot_product(vec1: List[int], vec2: List[int]) -> float:
    """
    Given 2 vectors, calculate the dot product between them
    :return: a scalar value
    """
    if len(vec1) != len(vec2):
        raise ValueError(f'Vectors must be same length to calculate dot product.\n'  # pragma: no cover
                         f'Vector 1 is size {len(vec1)}\nVector 2 is size {len(vec2)}')

    res = 0
    for i in range(len(vec1)):
        res += vec1[i] * vec2[i]
    return res


def get_region_cache_key(region_id: int) -> str:
    """
    Generate the cache key name for the sent region id
    :return: cache key name
    """
    return f'iaas_region_{region_id}'


def ip_is_private(ip: netaddr.IPAddress) -> bool:
    """
    Determine if provided IP Address is a private IP.
    0.0.0.0 represents any public IP Address.
    :param ip: netaddr IPAddress object
    :return: Boolean wether sent ip is private or not
    """

    return str(ip) != '0.0.0.0' and ip.is_global() is False


def int_to_hexadecimal(number: int) -> str:
    """
    Given a number, convert it to a hexadecimal
    """
    return f'{format(number, "x")}'


def get_vm_interface_mac_address(region_id: int, server_type_id: int, ip_address_id: int) -> str:
    """
    Given a region_id, server_type_id and ip_address_id, generate the region prefix part of a mac address
    e.g. XZ:XX:XX:YY:YY:YY
    X = region hexadecimal
    Y = ip_address_id hexadecimal
    Z = server_type_id
    Return the mac address for a VM interface based on the region and server type it is plcaed on
    """
    region_id_hex = int_to_hexadecimal(region_id).zfill(5)
    ip_hexadecimal = int_to_hexadecimal(ip_address_id).zfill(6)
    mac_address = (
        f'{region_id_hex[:1]}{server_type_id}:{region_id_hex[1:3]}:{region_id_hex[3:]}:{ip_hexadecimal[:2]}'
        f':{ip_hexadecimal[2:4]}:{ip_hexadecimal[4:]}'
    )

    return mac_address
