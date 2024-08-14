"""
Cloud Metrics for a given region
"""
# stdlib
from typing import Any, Dict
# libs
import netaddr
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.db.models import Count
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import state
from iaas.controllers import MetricsController
from iaas.models import (
    IPAddress,
    Project,
    Router,
    Server,
    Subnet,
    VM,
)
from iaas.permissions.metrics import Permissions
from iaas.serializers import (
    ServerMetricsSerializer,
    RouterMetricsSerializer,
)

__all__ = [
    'MetricsResource',
]


class MetricsResource(APIView):
    """
    Return the collection of metrics for the given region
    """

    def get(self, request: Request, region_id: int) -> Response:
        """
        summary: Get the collection of metrics
        description: |
            Retrieve a set of metrics for the current state

        path_params:
            region_id:
                description: The ID of the region to generate metrics for
                type: integer

        responses:
            200:
                description: A dataset of metrics for the specified region
            204:
                description: |
                    Empty response indicating that there are no new metrics to report.
                    Force a metrics update by sending `force=true` in the query parameters.
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        # Somehow ensure that the requested region is in fact a region
        with tracer.start_span('ensuring_valid_region', child_of=request.span):
            # Ensure that a Server or Router exist for the region
            server_exists = Server.objects.filter(region_id=region_id).exists()
            router_exists = Router.objects.filter(region_id=region_id).exists()
            # Ensure that at least one of the items exists
            if not (server_exists or router_exists):
                return Http404(error_code='iaas_metrics_read_001')

        # Start by checking permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, region_id)
            if err is not None:
                return err

        # Validate the get params before checking the run_icarus values
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = MetricsController(data=request.GET, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Check the run_icarus values
        force = controller.cleaned_data['force']
        with tracer.start_span('checking_run_icarus_flags', child_of=request.span) as span:
            span.set_tag('force', force)
            changed_projects = Project.objects.filter(run_icarus=True)

            # Send an empty response if no changes exist, and the force flag is false
            if not changed_projects.exists() and not force:
                return Response(status=status.HTTP_204_NO_CONTENT)

            # If we reach here, we're gonna run the metric gathering, so update the flags on all the changed projects
            changed_projects.update(run_icarus=False)

        # Fetch all the necessary objects from the DB
        data: Dict[str, Any] = {}
        with tracer.start_span('get_objects', child_of=request.span) as span:
            with tracer.start_span('get_vms', child_of=span):
                # We want a breakdown of states for the VMs, both for the total list and each server.
                # order_by() required to override default ordering which is applied after annotate
                data['vms'] = VM.objects.exclude(
                    state=state.CLOSED,
                ).filter(
                    server__region_id=region_id,
                    server__deleted__isnull=True,
                ).values(
                    'state',
                    'server_id',
                ).order_by().annotate(
                    count=Count('state'),
                )
                # Returns a list of dicts for every state + server combo, and how many vms match that pattern
                # e.g. [{"state": 4, "server_id": 16, "count": 1}, {"state": 4, "server_id": 9, "count": 1}]

            with tracer.start_span('get_servers', child_of=span) as db_span:
                # Just get all the servers in the region and serialize them
                objs = Server.objects.filter(region_id=region_id)

                with tracer.start_span('serializing_data', child_of=db_span) as serialize_span:
                    serialize_span.set_tag('num_objects', objs.count())
                    data['servers'] = ServerMetricsSerializer(instance=objs, many=True).data

            with tracer.start_span('get_routers', child_of=span) as db_span:
                # Just get all the servers in the region and serialize them
                objs = Router.objects.filter(region_id=region_id)

                with tracer.start_span('serializing_data', child_of=db_span) as serialize_span:
                    serialize_span.set_tag('num_objects', objs.count())
                    data['routers'] = RouterMetricsSerializer(instance=objs, many=True).data

            with tracer.start_span('get_subnets', child_of=span):
                # Just get all the servers in the region and serialize them
                subnets = Subnet.objects.filter(
                    ip_addresses__router__region_id=region_id,
                ).distinct().values(
                    'address_range',
                    'id',
                    'name',
                )

                # Then for each of these we need to get the space they can hold, and a count of how many ips they have
                for subnet in subnets:
                    subnet['capacity'] = netaddr.IPNetwork(subnet['address_range']).size - 2
                    subnet['ips_in_use'] = IPAddress.objects.filter(subnet_id=subnet['id']).count()

                data['subnets'] = subnets

        # Return the metrics data as requested
        return Response({'content': data})
