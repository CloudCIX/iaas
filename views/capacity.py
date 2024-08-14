"""
"""
# stdlib
from collections import defaultdict
from typing import Dict, List
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import (
    Server,
    ServerType,
    StorageType,
)

__all__ = [
    'CapacityCollection',
]

TERRABYTE = 1000


class CapacityCollection(APIView):
    """
    Handles methods regarding server capacities
    """

    def get(self, request: Request, region_id: int) -> Response:
        """
        summary: Find the largest VMs that a region can build

        description: Find the specs of the largest VMs that a User can build in a region.

        path_params:
            region_id:
                description: The region the User wants to inspect
                type: integer

        responses:
            200:
                description: Lists of VM resource dictionaries, categorised by Server Type and Storage Type
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_region_id', child_of=request.span) as span:
            response = Membership.cloud_bill.read(
                token=self.request.auth,
                address_id=region_id,
                target_address_id=self.request.user.address['id'],
                pk=None,
                span=span,
            )
            if response.status_code != 200:
                return Http400(error_code='iaas_capacity_list_101')

            if not response.json()['content']['is_region'] or not response.json()['content']['cloud_customer']:
                return Http400(error_code='iaas_capacity_list_102')

        with tracer.start_span('fetching_server_and_storage_types', child_of=request.span):
            server_types = ServerType.objects.exclude(name__icontains='phantom')
            storage_types = StorageType.objects.all()

        with tracer.start_span('calculating_maximum_capacity_of_servers', child_of=request.span) as span:
            data: Dict[str, Dict[str, List]] = defaultdict(dict)

            for server_type in server_types:
                for storage_type in storage_types:
                    servers = list(Server.objects.filter(
                        region_id=region_id,
                        type=server_type,
                        storage_type=storage_type,
                        enabled=True,
                    ))
                    if len(servers) == 0:
                        continue

                    with tracer.start_span('reducing_servers', child_of=span):
                        data[server_type.name][storage_type.name] = reduce(servers)

        return Response({'content': data})


def reduce(servers: List[Server]):

    if len(servers) > 1:

        for i, s1 in enumerate(servers):
            if s1 is None:
                continue
            k1 = s1.klinavicius
            k1[1] = min(2 * TERRABYTE, k1[1])

            for j, s2 in enumerate(servers[i + 1:], i + 1):
                if s2 is None:
                    continue
                k2 = s2.klinavicius
                k2[1] = min(2 * TERRABYTE, k2[1])

                comparison = 0
                for index in range(len(k1)):
                    if k1[index] >= k2[index]:
                        comparison += 1
                if comparison == len(k1):
                    # All values in k1 are greater than or equal to k2, so drop k2 from the list
                    servers[j] = None
                elif comparison == 0:
                    # All values in k2 are greater than k1, drop k1 from the list
                    servers[i] = None
                    break

    data: List[Dict[str, int]] = list()
    for s in servers:
        if s is None:
            continue
        k = s.klinavicius
        data.append({
            'ram': k[0],
            'storage': min(2 * TERRABYTE, k[1]),
            'cpu': k[2],
        })
    return data
