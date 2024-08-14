"""
Management of Region Storage Types
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import RegionStorageTypeCreateController
from iaas.models import RegionStorageType
from iaas.permissions.region_storage_type import Permissions

__all__ = [
    'RegionStorageTypeCollection',
    'RegionStorageTypeResource',
]


class RegionStorageTypeCollection(APIView):
    """
    Handles create method regarding RegionStorageType without ID being specified
    """

    def post(self, request: Request) -> Response:
        """
        summary: Create a new RegionStorageType entry

        description: Create a new RegionStorageType entry with data given by user

        responses:
            201:
                description: RegionStorageType record created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RegionStorageTypeCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.region = request.user.address['id']
            controller.instance.save()

        return Response(status=status.HTTP_201_CREATED)


class RegionStorageTypeResource(APIView):
    """
    Delete a given RegionStorageType instance
    """

    def delete(self, request: Request, storage_type_id: int) -> Response:
        """
        summary: Delete a specified RegionStorageType record

        description: |
            Attempt to delete a RegionStorageType record by the given `image_id`, returning a 404 if it doesn't exist

        path_params:
            storage_type_id:
                description: |
                    The storage_type_id for the requesting users address to delete the RegionStorageType object
                type: int

        responses:
            204:
                description: RegionStorageType record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = RegionStorageType.objects.get(
                    storage_type_id=storage_type_id,
                    region=request.user.address['id'],
                )
            except RegionStorageType.DoesNotExist:
                return Http404(error_code='iaas_region_storage_type_delete_001')

        with tracer.start_span('deleting_object', child_of=request.span):
            obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
