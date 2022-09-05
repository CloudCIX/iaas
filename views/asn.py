"""
Management of ASNs
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
from iaas.models import ASN
from iaas.controllers import (
    ASNListController,
    ASNUpdateController,
    ASNCreateController,
)
from iaas.permissions.asn import Permissions
from iaas.serializers import ASNSerializer

__all__ = [
    'ASNCollection',
    'ASNResource',
]


class ASNCollection(APIView):
    """
    Handles methods regarding ASN without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List ASNs
        description: |
            Retrieve a list of ASNs

        responses:
            200:
                description: A list of ASNs
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = ASNListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of ASNs using filters
        with tracer.start_span('get_objects', child_of=request.span):
            objs = ASN.objects.all()
            if request.user.member['id'] != 1:
                objs = objs.filter(member_id=request.user.member['id'])
            try:
                objs = objs.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_asn_list_001')

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
            data = ASNSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new ASN entry

        description: |
            Create a new ASN entry using data given by user.

        responses:
            201:
                description: ASN record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ASNCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request, controller.cleaned_data['number'])
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ASNSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class ASNResource(APIView):
    """
    Handles methods regarding ASN records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a ASN record by the given `pk`.
        description: Verify if a ASN record by the given `pk` exists.

        path_params:
            pk:
                description: The ID of the ASN.
                type: integer

        responses:
            200:
                description: Requested ASN exists.
            404:
                description: Requested ASN does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                ASN.objects.get(pk=pk)
            except ASN.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified ASN record

        description: |
            Attempt to read a ASN record by the given `id`, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the ASN record to be read
                type: integer

        responses:
            200:
                description: ASN record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = ASN.objects.get(id=pk)
            except ASN.DoesNotExist:
                return Http404(error_code='iaas_asn_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ASNSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified ASN record

        description: |
            Attempt to update a ASN record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the ASN to be updated
                type: integer

        responses:
            200:
                description: ASN record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = ASN.objects.get(id=pk)
            except ASN.DoesNotExist:
                return Http404(error_code='iaas_asn_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ASNUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ASNSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a ASN record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified ASN record

        description: |
            Attempt to delete a ASN record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the ASN to be deleted
                type: string

        responses:
            204:
                description: ASN record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = ASN.objects.get(id=pk)
            except ASN.DoesNotExist:
                return Http404(error_code='iaas_asn_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.cascade_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
