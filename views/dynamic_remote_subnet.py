"""
Cloud DynamicRemoteSubnets for a given region
"""
# stdlib
from typing import Any, Dict
# libs
from cloudcix_rest.exceptions import Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import DynamicRemoteSubnetController
from iaas.controllers.helpers import get_available_dynamic_remote_subnets, IAASException
from iaas.models import Router


__all__ = [
    'DynamicRemoteSubnetResource',
]


class DynamicRemoteSubnetResource(APIView):
    """
    Return the collection of DynamicRemoteSubnets for the given region
    """

    def get(self, request: Request, region_id: int) -> Response:
        """
        summary: Get the collection of DynamicRemoteSubnets
        description: |
            Retrieve a set of DynamicRemoteSubnets for the requested region

        path_params:
            region_id:
                description: The ID of the region to generate DynamicRemoteSubnets for
                type: integer

        responses:
            200:
                description: A dataset of DynamicRemoteSubnets for the specified region that are currently not in use
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                dynamic_remote_subnets:
                                    description: |
                                        A list of comma separated /24 subnets from 172.16.0.0/24 available to select
                                        as the remote subnet for a Dynamic Secure Connect VPN.
                                    type: List
            400: {}
            404: {}
        """
        tracer = settings.TRACER

        # Ensure that the requested region is in fact a region with router to build VPNs
        with tracer.start_span('ensuring_valid_region', child_of=request.span):
            # Ensure that a Router exist for the region
            if not Router.objects.filter(region_id=region_id).exists():
                return Http404(error_code='iaas_dynamic_remote_subnet_read_001')

        # Validate the get params before getting available dynamic remote subnets
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = DynamicRemoteSubnetController(data=request.GET, request=request, span=span)
            controller.is_valid()

            # Check the run_icarus values
            search_value = controller.cleaned_data.pop('dynamic_remote_subnet', None)

        with tracer.start_span('get_available_dynamic_remote_subnets', child_of=request.span):
            try:
                dynamic_remote_subnets = get_available_dynamic_remote_subnets(
                    region_id=region_id,
                    dynanmic_remote_subnet_error='iaas_dynamic_remote_subnet_read_002',
                    search_value=search_value,
                )
            except IAASException as e:
                return Http404(error_code=e.args[0])

        with tracer.start_span('serializing_data', child_of=request.span):
            data: Dict[str, Any] = {}
            data['dynamic_remote_subnets'] = dynamic_remote_subnets

        return Response({'content': data})
