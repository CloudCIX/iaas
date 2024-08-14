"""
Management of Storage Devices
"""
# python
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

# local
import iaas.state as states
from iaas import skus
from iaas.controllers import (
    StorageCreateController,
    StorageListController,
)
from iaas.models import (
    Storage,
    StorageHistory,
    VMHistory,
    VM,
)
from iaas.permissions.storage import Permissions
from iaas.serializers import StorageSerializer

__all__ = [
    'StorageCollection',
    'StorageResource',
]


class StorageCollection(APIView):
    """
    Handles methods regarding storage that do not require a specific id of a
    storage.
    """

    def get(self, request: Request, vm_id: int) -> Response:
        """
        summary: Retrieve a list of storages

        description: |
            Retrieve a list of storages within a vm.

        path_params:
            vm_id:
                description: The ID of the VM
                type: integer

        responses:
            200:
                description: A list of Storage records for the specified VM
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_vm', child_of=request.span):
            try:
                vm = VM.objects.get(pk=vm_id)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_storage_list_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.list(request, vm, span)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # validate with controller
            controller = StorageListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()
        # get storage object related to vm
        with tracer.start_span('get_objects', child_of=request.span) as span:
            # Get a list of Storage objects
            try:
                objs = Storage.objects.filter(
                    vm=vm,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_storage_list_002')

        with tracer.start_span('generating_metadata', child_of=request.span) as span:
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data.get('order'),
                'total_records': total_records,
                'warnings': warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = StorageSerializer(
                instance=objs,
                many=True,
            ).data
        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request, vm_id: int) -> Response:
        """
        summary: Create a new storage device

        description: Create a new storage device with data given by user

        path_params:
            vm_id:
                description: The ID of the VM
                type: integer

        responses:
            201:
                description: Storage device created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_vm', child_of=request.span):
            try:
                vm = VM.objects.get(pk=vm_id)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_storage_create_001')

            # Check that the VM in question can be updated
            if not vm.can_update():
                return Http400(error_code='iaas_storage_create_002')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request, vm)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StorageCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Do some additional validation here
        with tracer.start_span('checking_primary', child_of=request.span):
            # Because we 100% have to have a primary storage when we initially create a VM
            # We can only accept non-primary Storage objects through this view.
            if controller.cleaned_data['primary']:
                return Http400(error_code='iaas_storage_create_003')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.vm = vm
            controller.instance.save()

        with tracer.start_span('set_vm_to_update', child_of=request.span):
            state = states.RUNNING_UPDATE
            if vm.state == states.QUIESCED:
                state = states.QUIESCED_UPDATE
            vm.state = state
            vm.save()

        with tracer.start_span('get_gb_sku', child_of=request.span):
            if vm.server.storage_type_id in skus.STORAGE_SKU_MAP:
                gb_sku = skus.STORAGE_SKU_MAP[vm.server.storage_type_id]
            else:
                gb_sku = skus.DEFAULT

        with tracer.start_span('saving_vm_history', child_of=request.span):
            history = VMHistory.objects.create(
                vm=vm,
                modified_by=request.user.id,
                customer_address=request.user.address['id'],
                project_id=controller.instance.vm.project.pk,
                project_vm_name=f'{controller.instance.vm.project.name}_{controller.instance.vm.name}',
                state=state,
            )

        with tracer.start_span('generate_storage_history', child_of=request.span):
            StorageHistory.objects.create(
                gb_quantity=controller.instance.gb,
                gb_sku=gb_sku,
                storage_id=controller.instance.pk,
                vm_history=history,
            )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = StorageSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class StorageResource(APIView):
    """
    Handles methods regarding storage that do require a specific id of a
    storage.
    """

    def head(self, request: Request, vm_id: int, pk=int) -> Response:
        """
        summary: Verify a Storage record by the given `pk`.
        description: Verify if a Storage record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Storage.
                type: integer
            vm_id:
                description: The ID of the VM
                type: integer

        responses:
            200:
                description: Requested Storage exists and requesting User can access.
            404:
                description: Requesting user cannot access Storage if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_vm', child_of=request.span):
            try:
                vm = VM.objects.get(pk=vm_id)
            except VM.DoesNotExist:
                return Http404()

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                Storage.objects.get(pk=pk, vm=vm)
            except Storage.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, vm, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, vm_id: int, pk: int) -> Response:
        """
        summary: Retrieve the information for a specific storage device

        description: |
            Retrieve a specified storage device.

        path_params:
            pk:
                description: The ID of the storage record to be read
                type: integer
            vm_id:
                description: The ID of the VM
                type: integer

        responses:
            200:
                description: the storage device
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_vm', child_of=request.span):
            try:
                vm = VM.objects.get(pk=vm_id)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_storage_read_001')

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Storage.objects.get(pk=pk, vm=vm)
            except Storage.DoesNotExist:
                return Http404(error_code='iaas_storage_read_002')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, vm, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = StorageSerializer(instance=obj).data

        return Response({'content': data})
