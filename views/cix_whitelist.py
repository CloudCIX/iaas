"""
    Views for Whitelist
"""
# python
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
from iaas.controllers import (
    CIXWhitelistListController,
    CIXWhitelistCreateController,
    CIXWhitelistUpdateController,
)
from iaas.models import CIXWhitelist
from iaas.serializers import CIXWhitelistSerializer
from iaas.permissions.cix_whitelist import Permissions

__all__ = [
    'CIXWhitelistCollection',
    'CIXWhitelistResource',
]


class CIXWhitelistCollection(APIView):
    """
    Handles methods regarding CIXWhitelist records that do not require cidr to be specified.
    """

    def get(self, request: Request) -> Response:
        """
        summary: get whitelist records

        description: |
            Attempt to List CIDRs whitelisted by CIX.

        responses:
            200:
                description: CIXWhitelist record was listed successfully
            400: {}
        """
        tracer = settings.TRACER

        # Create a list controller to purse data
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CIXWhitelistListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = CIXWhitelist.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_cix_whitelist_list_001')

        # Gather metadata
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

            # Pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = CIXWhitelistSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: creates new whitelist entry

        description: |
            Attempt to create new whitelist entry.

        responses:
            201:
                description: CIXWhitelist record was created successfully
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CIXWhitelistCreateController(
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXWhitelistSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CIXWhitelistResource(APIView):
    """
    Handles methods regarding CIXWhitelist records that do require cidr to be specified.
    """

    def head(self, request: Request, cidr: str) -> Response:
        """
        summary: Verify a CIXWhitelist CIDR record by the given cidr

        description: |
            Verify if a CIXWhitelist CIDR record by the given `cidr` exists.

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            200:
                description: Requested CIXWhitelist CIDR record exists.
            404:
                description: Requested CIXWhitelist CIDR record does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                CIXWhitelist.objects.get(cidr=cidr)
            except CIXWhitelist.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, cidr: str) -> Response:
        """
        summary: reads details of Whitelisted CIDR using is cidr

        description: |
            Attempt to get information about the cidr.

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            200:
                description: CIXWhitelist record was read successfully
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXWhitelist.objects.get(cidr=cidr)
            except CIXWhitelist.DoesNotExist:
                return Http404(error_code='iaas_cix_whitelist_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXWhitelistSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, cidr: str, partial=False) -> Response:
        """
        summary: updates a whitelist with new info

        description: |
            Attempt to update information about the cidr.

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            200:
                description: CIXWhitelist record was updated successfully
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXWhitelist.objects.get(cidr=cidr)
            except CIXWhitelist.DoesNotExist:
                return Http404(error_code='iaas_cix_whitelist_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CIXWhitelistUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = CIXWhitelistSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, cidr: str) -> Response:
        """
        summary: updates the whitelist with a new cidr

        description: |
            Attempt to update information about the cidr.

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            200:
                description: CIXWhitelist record was updated successfully
            400: {}
            403: {}
        """

        return self.put(request, cidr, True)

    def delete(self, request: Request, cidr: str) -> Response:
        """
        summary: Delete a specified Whitelist record

        description: |
            Attempt to delete a whitelist record in the requesting `cidr`, returning a 404 if it does not exist

        path_params:
            cidr:
                description: address range representation
                type: string

        responses:
            204:
                description: Profile record was deleted successfully
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = CIXWhitelist.objects.get(cidr=cidr)
            except CIXWhitelist.DoesNotExist:
                return Http404(error_code='iaas_cix_whitelist_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
