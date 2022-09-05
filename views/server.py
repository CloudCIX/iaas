"""
Management of Servers
"""
# libs
from cloudcix_rest.exceptions import Http404, Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import Server
from iaas.permissions.server import Permissions
from iaas.controllers import ServerListController, ServerCreateController, ServerUpdateController
from iaas.serializers import ServerSerializer

__all__ = [
    'ServerCollection',
    'ServerResource',
]


class ServerCollection(APIView):

    def get(self, request: Request) -> Response:
        """
        summary: List Server records

        description: |
            Retrieve a list of Server records

        responses:
            200:
                description: A list of Server records
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ServerListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:
            kw = controller.cleaned_data['search']
            if request.user.id != 1:
                kw['region_id'] = request.user.address['id']
            try:
                objs = Server.objects.filter(
                    **kw,
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_server_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span) as span:
            total_records = objs.count()
            page = controller.cleaned_data['page']
            order = controller.cleaned_data['order']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'total_records': total_records,
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = ServerSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Server entry

        description: Create a new Server entry with data given by user

        responses:
            201:
                description: Server record created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ServerCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.region_id = request.user.address['id']
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ServerSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class ServerResource(APIView):
    """
    Handles methods regarding Servers that require the "pk" parameter
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Server record by the given `pk`.
        description: Verify if a Server record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Server.
                type: integer

        responses:
            200:
                description: Requested Server exists and requesting User can access.
            404:
                description: Requesting user cannot access Server if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Server.objects.get(pk=pk)
            except Server.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.head(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Server record

        description: |
            Attempt to read a Server record by the given `pk`, returning a 404 if does not exist

        path_params:
            pk:
                description: The ID of the Server record to be read
                type: integer

        responses:
            200:
                description: Server was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Server.objects.get(pk=pk)
            except Server.DoesNotExist:
                return Http404(error_code='iaas_server_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ServerSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Server

        description: |
            Attempt to update a Server by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the Server to be updated
                type: integer

        responses:
            200:
                description: Server was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Server.objects.get(pk=pk)
            except Server.DoesNotExist:
                return Http404(error_code='iaas_server_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ServerUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ServerSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Server
        """
        return self.put(request, pk, True)
