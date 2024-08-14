"""
Management of Device Types
"""

# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import DeviceTypeListController
from iaas.models import DeviceType
from iaas.serializers import DeviceTypeSerializer

__all__ = [
    'DeviceTypeCollection',
]


class DeviceTypeCollection(APIView):
    """
    Returns a list of the Device Types.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List device type records

        description: |
            Retrieve a list of DeviceType records, which indicate what DeviceTypes are available in CloudCIX

        responses:
            200:
                description: A list of DeviceType records
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        # Retrieve and validate the controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DeviceTypeListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()

        # Fetch items.
        with tracer.start_span('retrieving_objects', child_of=request.span):
            try:
                objs = DeviceType.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_device_type_list_001')

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
            data = DeviceTypeSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})
