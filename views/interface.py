"""
Management of Interfaces
"""

# stdlib
from datetime import datetime
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import InterfaceCreateController, InterfaceListController, InterfaceUpdateController
from iaas.models import Interface
from iaas.permissions.interface import Permissions
from iaas.serializers import InterfaceSerializer

__all__ = [
    'InterfaceCollection',
    'InterfaceResource',
]


class InterfaceCollection(APIView):
    """
    Returns a list of the physical interfaces on a Server.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Interface records

        description: Retrieve a list of Interface records

        responses:
            200:
                description: A list of Interface records
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.list(request)
            if error is not None:
                return error

        # Retrieve and validate the controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = InterfaceListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()

        # Fetch items.
        with tracer.start_span('retrieving_objects', child_of=request.span):
            kw = controller.cleaned_data['search']
            if request.user.id != 1:
                kw['server__region_id'] = request.user.address['id']
            try:
                objs = Interface.objects.filter(
                    **kw,
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_interface_list_001')

        # Generate Metadata.
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

        # Serialise data.
        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = InterfaceSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request):
        """
        summary: Add new Interface

        description: Creates a new Interface.

        responses:
            201:
                description: Interface was successfully created.
            400: {}
        """

        tracer = settings.TRACER

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.create(request)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = InterfaceCreateController(
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Save objects.
        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = InterfaceSerializer(instance=controller.instance)

        return Response({'content': serializer.data}, status=status.HTTP_201_CREATED)


class InterfaceResource(APIView):
    """
    Return an individual interface object.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify an Interface record by the given `pk`.
        description: Verify if an Interface record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Interface.
                type: integer

        responses:
            200:
                description: Requested Interface exists and requesting User can access.
            404:
                description: Requesting user cannot access Interface if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Interface.objects.get(pk=pk)
            except Interface.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.read(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Retrieve details of a specific interface.

        description: Retrieve the details of the interface with id 'pk'.

        path_params:
            pk:
                description: The ID of the interface to be retrieved.
                type: string

        responses:
            200:
                description: An interface is returned
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = Interface.objects.get(
                    deleted__isnull=True,
                    pk=pk,
                )
            except Interface.DoesNotExist:
                return Http404(error_code='iaas_interface_read_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.read(request, obj)
            if error is not None:
                return error

        # Serialise the data and return.
        with tracer.start_span('serializing_data', child_of=request.span):
            data = InterfaceSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Interface.

        description: Attempt to update an Interface record by the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The id of the Interface to be updated.
                type: integer

        responses:
            200:
                description: Interface was updated successfully.
            400: {}
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = Interface.objects.get(
                    pk=pk,
                )
            except Interface.DoesNotExist:
                return Http404(error_code='iaas_interface_update_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.update(request, obj)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = InterfaceUpdateController(
                data=request.data,
                request=request,
                partial=partial,
                span=span,
                instance=obj,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Save objects.
        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.save()

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = InterfaceSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update an Interface.
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Interface.

        description: Attempt to delete an Interface with the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The primary key of the interface to be deleted.
                type: string

        responses:
            204:
                description: Interface was deleted successfully.
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = Interface.objects.get(
                    deleted__isnull=True,
                    pk=pk,
                )
            except Interface.DoesNotExist:
                return Http404(error_code='iaas_interface_delete_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.delete(request, obj)
            if error is not None:
                return error

        # Update deleted timestamp.
        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
