"""
Management of IP Address Group
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
from iaas.models import IPAddressGroup
from iaas.controllers import (
    IPAddressGroupListController,
    IPAddressGroupUpdateController,
    IPAddressGroupCreateController,
)
from iaas.permissions.ip_address_group import Permissions
from iaas.serializers import IPAddressGroupSerializer


__all__ = [
    'IPAddressGroupCollection',
    'IPAddressGroupResource',
]


class IPAddressGroupCollection(APIView):
    """
    Handles methods regarding IP Address Group records that do not require a pk to be specified.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List IP Address Group records.

        description: |
            Retrieve a list of IP Address Groups that are owned by the users member or global .

        responses:
            200:
                description: A list of CIDRs
            400: {}
        """

        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = IPAddressGroupListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of IPAddressGroup records using filters
        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = IPAddressGroup.objects.filter(
                    member_id__in=[0, request.user.member_id],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_ip_address_group_list_001')

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
            data = IPAddressGroupSerializer(instance=objs, many=True).data

        # Generate and return response
        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new IP Address Group entry

        description: |
            Create a new IP Address Group entry using data given by user.

        responses:
            201:
                description: IP Address Group record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        # Validate the User data
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPAddressGroupCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request, controller.instance)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = IPAddressGroupSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class IPAddressGroupResource(APIView):
    """
    Handles methods regarding IP Address Group records that do require pk to be specified.
    """

    def head(self, request: Request, pk: int) -> Response:
        """
        summary: Verify a IP Address Group record by the given pk

        description: |
            Verify if a IP Address Group record by the given `pk` exists.

        path_params:
            pk:
                description: The ID of the IP Address Group.
                type: integer

        responses:
            200:
                description: Requested IP Address Group exists.
            404:
                description: Requested IP Address Group does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                IPAddressGroup.objects.get(pk=pk, member_id__in=[0, request.user.member_id])
            except IPAddressGroup.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified IP Address Group record

        description: |
            Attempt to read a IP Address Group record by the given `pk`, returning a 404 if it does not exist

        path_params:
            pk:
                description: The ID of the IP Address Group.
                type: integer

        responses:
            200:
                description: IP Address Group record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddressGroup.objects.get(pk=pk, member_id__in=[0, request.user.member_id])
            except IPAddressGroup.DoesNotExist:
                return Http404(error_code='iaas_ip_address_group_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = IPAddressGroupSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified IPAddressGroup record

        description: |
            Attempt to update a IPAddressGroup record by the given `cidr`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the IPAddressGroup.
                type: integer

        responses:
            200:
                description: IPAddressGroup record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddressGroup.objects.get(pk=pk, member_id__in=[0, request.user.member_id])
            except IPAddressGroup.DoesNotExist:
                return Http404(error_code='iaas_ip_address_group_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPAddressGroupUpdateController(instance=obj, data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = IPAddressGroupSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a IPAddressGroup record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified IPAddressGroup record

        description: |
            Attempt to delete a IPAddressGroup record by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the IPAddressGroup.
                type: integer

        responses:
            204:
                description: IPAddressGroup record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddressGroup.objects.get(pk=pk, member_id__in=[0, request.user.member_id])
            except IPAddressGroup.DoesNotExist:
                return Http404(error_code='iaas_ip_address_group_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.now()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
