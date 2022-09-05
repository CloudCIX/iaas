"""
    Views for Pool IP
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
from iaas.controllers import (
    PoolIPListController,
    PoolIPCreateController,
    PoolIPUpdateController,
)
from iaas.models import PoolIP
from iaas.serializers import PoolIPSerializer
from iaas.permissions.pool_ip import Permissions

__all__ = [
    'PoolIPCollection',
    'PoolIPResource',
]


class PoolIPCollection(APIView):
    """
    Handles methods regarding PoolIP records that do not require id to be specified.
    """

    def get(self, request: Request) -> Response:
        """
        summary: Get a list of PoolIP records.

        description: |
            Get a list of PoolIP records.

            PoolIP records link domain names to our OOB IPMI pool.
            These IP addresses are used in the IPMI process to provide domain names for the User to connect to.

        responses:
            200:
                description: A list of PoolIP records.
            400: {}
        """
        tracer = settings.TRACER

        # List IPs in the OOB Pool
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PoolIPListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = PoolIP.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_pool_ip_list_001')

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
            data = PoolIPSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new PoolIP record

        description: |
            Add a new PoolIP record, representing a new IP address in our OOB pool.

        responses:
            201:
                description: PoolIP record was created successfully
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PoolIPCreateController(
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
            serializer = PoolIPSerializer(instance=controller.instance)

        return Response({'content': serializer.data}, status=status.HTTP_201_CREATED)


class PoolIPResource(APIView):
    """
    Handles methods regarding PoolIP records that do require id to be specified.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a PoolIP record by the given `pk`.
        description: Verify if a PoolIP record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the PoolIP.
                type: integer

        responses:
            200:
                description: Requested PoolIP exists and requesting User can access.
            404:
                description: PoolIP does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                PoolIP.objects.get(pk=pk)
            except PoolIP.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a PoolIP record.

        description: |
            Fetch the details of a specific PoolIP record.

        path_params:
            pk:
                description: The ID of the PoolIP record to be read.
                type: integer

        responses:
            200:
                description: PoolIP record was read successfully
            404: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = PoolIP.objects.get(id=pk)
            except PoolIP.DoesNotExist:
                return Http404(error_code='iaas_pool_ip_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = PoolIPSerializer(instance=obj)

        return Response({'content': serializer.data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a PoolIP record.

        description: |
            Attempt to update the information in a given PoolIP record.

        path_params:
            pk:
                description: The ID of the PoolIP record to be updated.
                type: integer

        responses:
            200:
                description: PoolIP record was updated successfully
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
                obj = PoolIP.objects.get(id=pk)
            except PoolIP.DoesNotExist:
                return Http404(error_code='iaas_pool_ip_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PoolIPUpdateController(
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
            serializer = PoolIPSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Partial Update of a PoolIP record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a PoolIP record.

        description: |
            Attempt to remove an IP address from the OOB pool by deleting a PoolIP record.

        path_params:
            pk:
                description: The ID of the PoolIP record to be deleted.
                type: integer

        responses:
            204:
                description: PoolIP record was deleted successfully
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = PoolIP.objects.get(id=pk)
            except PoolIP.DoesNotExist:
                return Http404(error_code='iaas_pool_ip_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
