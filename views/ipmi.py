"""
    Views for IPMI
"""
# python
from datetime import datetime
from typing import Optional
# libs
from cloudcix_rest.views import APIView
from cloudcix_rest.exceptions import Http400, Http404, Http503
from django.conf import settings
from django.core.exceptions import ValidationError
from jnpr.junos import Device
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import IPMIListController, IPMICreateController
from iaas.models import AppSettings, IPMI, PoolIP
from iaas.permissions.ipmi import Permissions
from iaas.serializers import IPMISerializer

__all__ = [
    'IPMICollection',
    'IPMIResource',
]


def _get_juniper_device() -> Optional[Device]:  # pragma: no cover
    """
    Using the values in settings, create an instance of a jnpr Device and return it.
    If not in an environment where a router is available, return None instead.
    """
    app_settings = AppSettings.objects.filter()[0]
    if app_settings.ipmi_credentials is None or app_settings.ipmi_host is None \
            or app_settings.ipmi_username is None:
        return Http404(error_code='iaas_ipmi_get_juniper_device_001')

    kw = {
        'host': app_settings.ipmi_host,
        'user': app_settings.ipmi_username,
        'password': app_settings.ipmi_credentials,
        'port': 22,
    }

    return Device(**kw)


class IPMICollection(APIView):
    """
    Handles methods regarding IPMI records that do not require id to be specified.
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of IPMI records.

        description: |
            Attempt to retrieve a list of IPMI records that are currently in use from the database.

        responses:
            200:
                description: A list of IPMI records.
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPMIListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            objs = IPMI.objects.all()
            if request.user.member['id'] != 1:
                objs = objs.filter(customer_ip__subnet__address_id=request.user.address['id'])
            try:
                objs = objs.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_ipmi_list_001')

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
            data = IPMISerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new IPMI record.

        description: |
            Attempt to create a new IPMI record both in the database and in the router.
            HTTP 503 errors will be returned if any errors occur when interacting with the router itself.

        responses:
            201:
                description: IPMI record was created successfully
            400: {}
            403: {}
            503:
                description: An error occurred when writing the IPMI rules to the Router
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPMICreateController(
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_objects', child_of=request.span):
            # Give the IPMI record the least recently used pool ip record to use
            controller.instance.pool_ip = PoolIP.objects.order_by('updated')[0]
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('connecting_to_router', child_of=request.span):
            device = _get_juniper_device()
            if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
                err = controller.instance.deploy_to_router(device)
                if err is not None:
                    # Delete the sent record and return a 503 error
                    controller.instance.delete()
                    return Http503(error_code=err)

        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = IPMISerializer(instance=controller.instance)

        return Response({'content': serializer.data}, status=status.HTTP_201_CREATED)


class IPMIResource(APIView):
    """
    Handles methods regarding IPMI records that do not require id to be specified.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a IPMI record by the given `pk`.
        description: Verify if a IPMI record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the IPMI.
                type: integer

        responses:
            200:
                description: Requested IPMI exists and requesting User can access.
            404:
                description: Requesting user cannot access IPMI if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPMI.objects.get(pk=pk)
            except IPMI.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.head(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read an IPMI record

        description: |
            Attempt to read the details of an IPMI record based on the sent `pk` value.

        path_params:
            pk:
                description: The ID of the IPMI record to read.
                type: integer

        responses:
            200:
                description: IPMI record was listed successfully
            404: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('get_objects', child_of=request.span):
            try:
                obj = IPMI.objects.get(pk=pk)
            except IPMI.DoesNotExist:
                return Http404(error_code='iaas_ipmi_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = IPMISerializer(instance=obj).data

        return Response({'content': data})

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a chosen IPMI record.

        description: |
            Attempt to delete an IPMI record from both the database and our Routers.
            This view will return HTTP 404 errors if the sent `pk` value is incorrect, or 503 errors if a hardware issue
            occurs.

        path_params:
            pk:
                description: The ID of the IPMI record to delete.
                type: integer

        responses:
            204:
                description: IPMI record was deleted successfully
            403: {}
            404: {}
            503:
                description: An error occurred when writing the IPMI rules to the Router
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPMI.objects.get(pk=pk)
            except IPMI.DoesNotExist:
                return Http404(error_code='iaas_ipmi_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('connecting_to_router', child_of=request.span):
            device = _get_juniper_device()
            if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
                err = obj.remove_from_router(device)
                if err is not None:
                    # Return a 503 error
                    return Http503(error_code=err)

        with tracer.start_span('saving_object', child_of=request.span):
            obj.removed = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
