"""
Management of Images
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import ImageListController, ImageUpdateController
from iaas.models import Image, RegionImage
from iaas.permissions.image import Permissions
from iaas.serializers import ImageSerializer

__all__ = [
    'ImageCollection',
    'ImageResource',
]


class ImageCollection(APIView):
    """
    Returns a list of the images available for VMs.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Image records

        description: Retrieve a list of Image records

        responses:
            200:
                description: A list of Image records
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        # Retrieve and validate the controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ImageListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()

        with tracer.start_span('updating_search_filters', child_of=request.span):
            if not request.user.id == 1:
                controller.cleaned_data['search']['public'] = True

        # Fetch items.
        with tracer.start_span('retrieving_objects', child_of=request.span):
            try:
                objs = Image.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_image_list_001')

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
            data = ImageSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class ImageResource(APIView):
    """
    Return an individual Image object.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify an Image record by the given `pk`.
        description: Verify if an Image record by the given `pk` exists.

        path_params:
            pk:
                description: The ID of the Image.
                type: integer

        responses:
            200:
                description: Requested Image exists.
            404:
                description: Requested Image does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_object', child_of=request.span):
            params = {'pk': pk}
            if not request.user.id == 1:
                params['public'] = True

            try:
                Image.objects.get(**params)
            except Image.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Retrieve details of a specific Image.

        description: Retrieve the details of the Image with id 'pk'.

        path_params:
            pk:
                description: The ID of the Image to be retrieved.
                type: integer

        responses:
            200:
                description: An Image is returned
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            params = {'pk': pk}
            if not request.user.id == 1:
                params['public'] = True

            try:
                obj = Image.objects.get(**params)
            except Image.DoesNotExist:
                return Http404(error_code='iaas_image_read_001')

        # Serialise the data and return.
        with tracer.start_span('serializing_data', child_of=request.span):
            data = ImageSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Image.

        description: Attempt to update an Image record by the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The id of the Image to be updated.
                type: integer

        responses:
            200:
                description: Image was updated successfully.
            400: {}
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = Image.objects.get(pk=pk)
            except Image.DoesNotExist:
                return Http404(error_code='iaas_image_update_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.update(request, obj)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ImageUpdateController(
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
            controller.instance.regions.all().delete()
            regions = [
                RegionImage(image=controller.instance, region=region)
                for region in controller.cleaned_data.pop('regions', [])
            ]
            RegionImage.objects.bulk_create(regions)

        # Save objects.
        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.save()

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = ImageSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update an Image.
        """
        return self.put(request, pk, True)
