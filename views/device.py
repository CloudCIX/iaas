"""
Management of Devices
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import (
    DeviceCreateController,
    DeviceListController,
    DeviceUpdateController,
)
from iaas.models import Device
from iaas.permissions.device import Permissions
from iaas.serializers import DeviceSerializer

__all__ = [
    'DeviceCollection',
    'DeviceResource',
]


class DeviceCollection(APIView):
    """
    Handles methods regarding Device without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Devices
        description: Retrieve a list of Devices

        responses:
            200:
                description: A list of Devices
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = DeviceListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of Allocations using filters
        with tracer.start_span('get_objects', child_of=request.span):
            kw = controller.cleaned_data['search']
            if request.user.id != 1:
                kw['server__region_id'] = request.user.address['id']
            try:
                objs = Device.objects.filter(
                    **kw,
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_device_list_001')

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
            data = DeviceSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Device entry

        description: Create a new Device entry using data given by user.

        responses:
            201:
                description: Device record was created successfully
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
            controller = DeviceCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = DeviceSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class DeviceResource(APIView):
    """
    Handles methods regarding Device records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Device record by the given `pk`.
        description: Verify if a Device record by the given `pk` exists.

        path_params:
            pk:
                description: The ID of the Device.
                type: integer

        responses:
            200:
                description: Requested Device exists.
            404:
                description: Requested Device does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Device.objects.get(pk=pk)
            except Device.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.read(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified Device record

        description: |
            Attempt to read a Device record by the given `id`, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Device record to be read
                type: integer

        responses:
            200:
                description: Device record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Device.objects.get(id=pk)
            except Device.DoesNotExist:
                return Http404(error_code='iaas_device_read_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = DeviceSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified Device record

        description: |
            Attempt to update a Device record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Device to be updated
                type: integer

        responses:
            200:
                description: Device record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Device.objects.get(id=pk, server__region_id=request.user.address['id'])
            except Device.DoesNotExist:
                return Http404(error_code='iaas_device_update_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DeviceUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            detach_device = controller.cleaned_data.pop('detach_device', False)
            if detach_device:
                controller.instance.vm_id = None
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = DeviceSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a ASN record
        """
        return self.put(request, pk, True)
