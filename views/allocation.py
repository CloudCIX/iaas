"""
Management of Allocations
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import Allocation
from iaas.controllers import (
    AllocationListController,
    AllocationUpdateController,
    AllocationCreateController,
)
from iaas.permissions.allocation import Permissions
from iaas.serializers import AllocationSerializer

__all__ = [
    'AllocationCollection',
    'AllocationResource',
]


class AllocationCollection(APIView):
    """
    Handles methods regarding Allocation without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Allocations
        description: |
            Retrieve a list of Allocations

        responses:
            200:
                description: A list of Allocations
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = AllocationListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of Allocations using filters
        with tracer.start_span('get_objects', child_of=request.span):
            objs = Allocation.objects.all()
            if request.user.address['id'] != 1:
                objs = Allocation.objects.filter(
                    Q(asn__member_id=request.user.member['id'])
                    | Q(address_id=request.user.address['id']),
                )
            try:
                objs = objs.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_allocation_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
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
            # Handle pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = AllocationSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Allocation entry

        description: |
            Create a new Allocation entry using data given by user.

        responses:
            201:
                description: Allocation record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AllocationCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = AllocationSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AllocationResource(APIView):
    """
    Handles methods regarding Allocation records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify an Allocation record by the given `pk`.
        description: Verify if an Allocation record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Allocation.
                type: integer

        responses:
            200:
                description: Requested Allocation exists and requesting User can access.
            404:
                description: Requesting user cannot access Allocation if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Allocation.objects.get(pk=pk)
            except Allocation.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.head(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified Allocation record

        description: |
            Attempt to read a Allocation record by the given `id`, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Allocation record to be read
                type: integer

        responses:
            200:
                description: Allocation record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Allocation.objects.get(id=pk)
            except Allocation.DoesNotExist:
                return Http404(error_code='iaas_allocation_read_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = AllocationSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified Allocation record

        description: |
            Attempt to update an Allocation record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Allocation to be updated
                type: integer

        responses:
            200:
                description: Allocation record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Allocation.objects.get(id=pk)
            except Allocation.DoesNotExist:
                return Http404(error_code='iaas_allocation_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AllocationUpdateController(
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
            data = AllocationSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update an Allocation record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Allocation record

        description: |
            Attempt to delete an Allocation record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Allocation to be deleted
                type: string

        responses:
            204:
                description: Allocation record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Allocation.objects.get(id=pk)
            except Allocation.DoesNotExist:
                return Http404(error_code='iaas_allocation_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.cascade_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
