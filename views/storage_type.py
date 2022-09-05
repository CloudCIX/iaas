"""
Management of Storage Types
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import StorageTypeListController, StorageTypeUpdateController
from iaas.models import StorageType, RegionStorageType
from iaas.permissions.storage_type import Permissions
from iaas.serializers import StorageTypeSerializer

__all__ = [
    'StorageTypeCollection',
    'StorageTypeResource',
]


class StorageTypeCollection(APIView):
    """
    Returns a list of the storage types.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List storage type records

        description: |
            Retrieve a list of StorageType records, which indicate what StorageTypes are available in CloudCIX, as well
            as what regions the StorageTypes are available for use in.

        responses:
            200:
                description: A list of StorageType records
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        # Retrieve and validate the controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StorageTypeListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()

        # Fetch items.
        with tracer.start_span('retrieving_objects', child_of=request.span):
            try:
                objs = StorageType.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_storage_type_list_001')

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
            data = StorageTypeSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class StorageTypeResource(APIView):
    """
    Return an individual storage type object.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Storage Type record by the given `pk`.
        description: Verify if a Storage Type record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Storage Type .
                type: integer

        responses:
            200:
                description: Requested Storage Type  exists and requesting User can access.
            404:
                description: Requesting user cannot access Storage Type  if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                StorageType.objects.get(pk=pk)
            except StorageType.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Retrieve details of a specific storage type.

        description: Retrieve the details of the storage type with id 'pk'.

        path_params:
            pk:
                description: The ID of the storage type to be retrieved.
                type: integer

        responses:
            200:
                description: An storage type is returned
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = StorageType.objects.get(
                    pk=pk,
                )
            except StorageType.DoesNotExist:
                return Http404(error_code='iaas_storage_type_read_001')

        # Serialise the data and return.
        with tracer.start_span('serializing_data', child_of=request.span):
            data = StorageTypeSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified storage type.

        description: Attempt to update an storage type record by the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The id of the storage type to be updated.
                type: integer

        responses:
            200:
                description: Storage type was updated successfully.
            400: {}
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = StorageType.objects.get(
                    pk=pk,
                )
            except StorageType.DoesNotExist:
                return Http404(error_code='iaas_storage_type_update_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.update(request, obj)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StorageTypeUpdateController(
                data=request.data,
                request=request,
                partial=partial,
                span=span,
                instance=obj,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Unlinking and relinking regions
        with tracer.start_span('adding_images_to_regions', child_of=request.span):
            obj.regions.all().delete()
            regions = [
                RegionStorageType(storage_type=obj, region=region)
                for region in controller.cleaned_data.pop('regions')
            ]
            RegionStorageType.objects.bulk_create(regions)
            obj.refresh_from_db()

        # Save objects.
        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.save()

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = StorageTypeSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a storage type.
        """
        return self.put(request, pk, True)
