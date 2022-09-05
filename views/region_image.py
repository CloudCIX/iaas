"""
Management of Region Images
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import RegionImageCreateController
from iaas.models import RegionImage
from iaas.permissions.region_image import Permissions

__all__ = [
    'RegionImageCollection',
    'RegionImageResource',
]


class RegionImageCollection(APIView):
    """
    Handles create method regarding RegionImage without ID being specified
    """

    def post(self, request: Request) -> Response:
        """
        summary: Create a new RegionImage entry

        description: Create a new RegionImage entry with data given by user

        responses:
            201:
                description: RegionImage record created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RegionImageCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.region = request.user.address['id']
            controller.instance.save()

        return Response(status=status.HTTP_201_CREATED)


class RegionImageResource(APIView):
    """
    Delete a given RegionImage instance
    """

    def delete(self, request: Request, image_id: int) -> Response:
        """
        summary: Delete a specified RegionImage record

        description: |
            Attempt to delete a RegionImage record by the given `image_id`, returning a 404 if it doesn't exist

        path_params:
            image_id:
                description: The image_id for the requesting users address to delete the RegionImage object
                type: int

        responses:
            204:
                description: RegionImage record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = RegionImage.objects.get(
                    image_id=image_id,
                    region=request.user.address['id'],
                )
            except RegionImage.DoesNotExist:
                return Http404(error_code='iaas_region_image_delete_001')

        with tracer.start_span('deleting_object', child_of=request.span):
            obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
