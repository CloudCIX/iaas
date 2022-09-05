"""
Views for IPAddress
"""
# stdlib
from typing import Optional
# libs
import netaddr
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import (
    IPAddressListController,
    IPAddressCreateController,
    IPAddressUpdateController,
)
from iaas.models import ASN, IPAddress, Project, VirtualRouter
from iaas.permissions.ip_address import Permissions
from iaas.serializers import IPAddressSerializer

__all__ = [
    'IPAddressCollection',
    'IPAddressResource',
]


class IPAddressCollection(APIView):
    """
    Handles methods regarding IP address.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List IPAddress records.

        description: |
            Retrieve a list of IPAddress records, filtered by any filters that the User has sent.

        responses:
            200:
                description: A list of IPAddress records.
            400: {}
        """

        tracer = settings.TRACER

        # List IPs
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPAddressListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Handle the cloud filtering by setting up extra filters for IPs in the cloud
        cloud_filtering: Optional[Q] = None
        if request.user.robot:
            # Robot; pseudo asns of projects in its region or those in a Subnet belonging to their address
            numbers = Project.objects.filter(region_id=request.user.address['id']).values_list('pk', flat=True)
            numbers = [pk + ASN.pseudo_asn_offset for pk in numbers]

            cloud_filtering = Q(
                subnet__allocation__asn__number__in=numbers,
            ) | Q(
                subnet__address_id=request.user.address['id'],
            )
        elif request.user.id != 1:
            # IPs related to their Projects. These are simply any IP in a pseudo ASN belonging to their Member or
            # those in a Subnet belonging to their Address
            cloud_filtering = Q(
                subnet__allocation__asn__member_id=request.user.member['id'],
                subnet__allocation__asn__number__gt=ASN.pseudo_asn_offset,
            ) | Q(
                subnet__address_id=request.user.address['id'],
            )

        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = IPAddress.objects.filter(
                    **controller.cleaned_data['search'],
                )

                if cloud_filtering is not None:
                    objs = objs.filter(cloud_filtering)

                objs = objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_ip_address_list_001')

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
            data = IPAddressSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new IPAddress record.

        description: |
            Create a new IPAddress record using data provided by the User.

        responses:
            201:
                description: New IPAddress record was successfully created.
            400: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPAddressCreateController(
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.create(request, controller.instance.subnet, controller.instance.cloud)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = IPAddressSerializer(instance=controller.instance).data

        return Response({'content': serializer}, status=status.HTTP_201_CREATED)


class IPAddressResource(APIView):
    """
    Handles methods regarding IPAddress records that do require id to be specified.
    """

    def head(self, request: Request, pk: int) -> Response:
        """
        summary: Verify a IP Address record by the given `pk`.
        description: Verify if a IP Address record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the IP Address.
                type: integer

        responses:
            200:
                description: Requested IP Address exists and requesting User can access.
            404:
                description: Requesting user cannot access IP Address if it exists.
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddress.objects.get(pk=pk)
            except IPAddress.DoesNotExist:
                return Http404()

        project = None
        if obj.cloud:
            # 1. Private IP for VM
            # 2. Floating IP for virtual router
            # 3. Floating IP natted to private IP for VM
            with tracer.start_span('retrieve_project_for_cloud_ip', child_of=request.span):
                if netaddr.IPAddress(obj.address).is_private():
                    # 1. Private IP for VM
                    project = obj.vm.project
                else:
                    # If the IP Address is a Public cloud IP, it is either a floating IP for a VM or the virtual
                    # router's IP.
                    private_ip = IPAddress.objects.filter(public_ip=obj.id)

                    if len(private_ip) == 0:
                        # 2. Floating IP for virtual router
                        virtual_router = VirtualRouter.objects.filter(ip_address=obj)
                        project = virtual_router[0].project
                    elif len(private_ip) == 1:
                        # 3. Floating IP natted to private IP for VM
                        project = private_ip[0].vm.project
                    else:  # pragma: no cover
                        # More than 1 IP returned!
                        return Http404()

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.head(request, obj, project)
            if err is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Reads an IP Address

        description: |
            Attempt to read an IP Address using the `pk` supplied by the User.

        path_params:
            pk:
                type: integer

        responses:
            200:
                description: IPAddress record was read successfully
            400: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddress.objects.get(pk=pk)
            except IPAddress.DoesNotExist:
                return Http404(error_code='iaas_ip_address_read_001')

        project = None
        if obj.cloud:
            # 1. Private IP for VM
            # 2. Floating IP for virtual router
            # 3. Floating IP natted to private IP for VM
            with tracer.start_span('retrieve_project_for_cloud_ip', child_of=request.span):
                if netaddr.IPAddress(obj.address).is_private():
                    # 1. Private IP for VM
                    project = obj.vm.project
                else:
                    # If the IP Address is a Public cloud IP, it is either a floating IP for a VM or the virtual
                    # router's IP.
                    private_ip = IPAddress.objects.filter(public_ip=obj.id)

                    if len(private_ip) == 0:
                        # 2. Floating IP for virtual router
                        virtual_router = VirtualRouter.objects.filter(ip_address=obj)
                        project = virtual_router[0].project
                    elif len(private_ip) == 1:
                        # 3. Floating IP natted to private IP for VM
                        project = private_ip[0].vm.project
                    else:  # pragma: no cover
                        # More than 1 IP returned!
                        return Http400(error_code='iaas_ip_address_read_002')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj, project)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = IPAddressSerializer(instance=obj).data

        return Response({'content': serializer})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Updates an IPAddress record.

        description: |
            Attempt to update an IPAddress record using the `pk` given by the User.

        path_params:
            pk:
                type: integer

        responses:
            200:
                description: IPAddress record was updated successfully
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddress.objects.get(pk=pk)
            except IPAddress.DoesNotExist:
                return Http404(error_code='iaas_ip_address_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPAddressUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = IPAddressSerializer(instance=controller.instance).data

        return Response({'content': serializer})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to update an IP Address partially.
        """

        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete an IPAddress record.

        description: |
            Attempt to delete an IPAddress record using the `pk `sent by the User.

        path_params:
            pk:
                type: integer

        responses:
            204:
                description: IPAddress record was deleted successfully.
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = IPAddress.objects.get(pk=pk)
            except IPAddress.DoesNotExist:
                return Http404(error_code='iaas_ip_address_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.cascade_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
