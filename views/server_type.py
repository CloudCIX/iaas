"""
Views for Server Type
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import ServerType
from iaas.controllers import ServerTypeListController
from iaas.serializers import ServerTypeSerializer

__all__ = [
    'ServerTypeCollection',
    'ServerTypeResource',
]


class ServerTypeCollection(APIView):
    """
    Handles methods regarding ServerType that do not require a specific id
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Server Type

        description: |
            Retrieve a list of Server Type which represent the the type of server e.g. HyperV Host or KVM Host.

        responses:
            200:
                description: A list of ServerType records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ServerTypeListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = ServerType.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_server_type_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'total_records': objs.count(),
                'warnings': warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = ServerTypeSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class ServerTypeResource(APIView):
    """
    Handles methods regarding Server Type that do require a specific id
    """
    def head(self, request: Request, pk: int) -> Response:
        """
        summary: Verify a Server Type record by the given `pk`.
        description: Verify if a Server Type record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Server Type.
                type: integer

        responses:
            200:
                description: Requested Server Type exists and requesting User can access.
            404:
                description: Requesting user cannot access Server Type if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                ServerType.objects.get(pk=pk)
            except ServerType.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a Server Type

        description: |
            Retrieve and reads a Server Type which represent the the type of server e.g. HyperV Host or KVM Host.

        path_params:
            pk:
                description: The id of the Server Type to Read
                type: integer

        responses:
            200:
                description: Reads a Server Type
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = ServerType.objects.get(pk=pk)
            except ServerType.DoesNotExist:
                return Http404(error_code='iaas_server_type_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ServerTypeSerializer(instance=obj).data

        return Response({'content': data})
