"""
Management of Blacklist
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
from iaas.models import CIXBlacklist
from iaas.controllers import (
    CIXBlacklistListController,
    CIXBlacklistUpdateController,
    CIXBlacklistCreateController,
)
from iaas.permissions.cix_blacklist import Permissions
from iaas.serializers import CIXBlacklistSerializer

__all__ = [
    'CIXBlacklistCollection',
    'CIXBlacklistResource',
]


class CIXBlacklistCollection(APIView):
    """
    Handles methods regarding CIX Blacklist records that do not require cidr to be specified.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List CIDRs recognised as malicious by CIX.

        description: |
            Retrieve a list of CIDRs recognised as malicious by CIX.

        responses:
            200:
                description: A list of CIDRs
            400: {}
        """

        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = CIXBlacklistListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of CIXBlacklist records using filters
        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = CIXBlacklist.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_cix_blacklist_list_001')

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
            data = CIXBlacklistSerializer(instance=objs, many=True).data

        # Generate and return response
        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new CIXBlacklist entry

        description: |
            Create a new CIXBlacklist entry using data given by user.

        responses:
            201:
                description: CIXBlacklist record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        # Validate the User data
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CIXBlacklistCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXBlacklistSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CIXBlacklistResource(APIView):
    """
    Handles methods regarding CIXBlacklist records that do require cidr to be specified.
    """

    def head(self, request: Request, cidr: str) -> Response:
        """
        summary: Verify a CIXBlacklist CIDR record by the given cidr

        description: |
            Verify if a CIXBlacklist CIDR record by the given `cidr` exists.

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            200:
                description: Requested CIXBlacklist CIDR exists.
            404:
                description: Requested CIXBlacklist CIDR does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                CIXBlacklist.objects.get(cidr=cidr)
            except CIXBlacklist.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, cidr: str) -> Response:
        """
        summary: Read the details of a specified CIXBlacklist record

        description: |
            Attempt to read a CIXBlacklist record by the given `cidr`, returning a 404 if it does not exist

        path_params:
            cidr:
                description: The cidr of the CIXBlacklist record to be read
                type: string

        responses:
            200:
                description: CIXBlacklist record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXBlacklist.objects.get(cidr=cidr)
            except CIXBlacklist.DoesNotExist:
                return Http404(error_code='iaas_cix_blacklist_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXBlacklistSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, cidr: str, partial=False) -> Response:
        """
        summary: Update the details of a specified CIXBlacklist record

        description: |
            Attempt to update a CIXBlacklist record by the given `cidr`, returning a 404 if it doesn't exist

        path_params:
            cidr:
                description: The cidr of the CIXBlacklist to be updated
                type: string

        responses:
            200:
                description: CIXBlacklist record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXBlacklist.objects.get(cidr=cidr)
            except CIXBlacklist.DoesNotExist:
                return Http404(error_code='iaas_cix_blacklist_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CIXBlacklistUpdateController(instance=obj, data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXBlacklistSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, cidr: str) -> Response:
        """
        Attempt to partially update a CIXBlacklist record
        """
        return self.put(request, cidr, True)

    def delete(self, request: Request, cidr: str) -> Response:
        """
        summary: Delete a specified CIXBlacklist record

        description: |
            Attempt to delete a CIXBlacklist record by the given `cidr`, returning a 404 if it doesn't exist

        path_params:
            cidr:
                description: The cidr of the CIXBlacklist to be deleted
                type: string

        responses:
            204:
                description: CIXBlacklist record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXBlacklist.objects.get(cidr=cidr)
            except CIXBlacklist.DoesNotExist:
                return Http404(error_code='iaas_cix_blacklist_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
