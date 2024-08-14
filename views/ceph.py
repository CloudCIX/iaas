"""
Management of Ceph devices
"""
# libs
from cloudcix_rest.exceptions import Http400, Http403, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import resource_type, state
from iaas.controllers import (
    CephCreateController,
    CephListController,
    CephUpdateController,
)
from iaas.models import Resource
from iaas.permissions.ceph import Permissions
from iaas.serializers.resource import ResourceSerializer
from iaas.utils import get_addresses_in_member

__all__ = [
    'CephCollection',
    'CephResource',
]


class CephCollection(APIView):
    """
    Handles methods regarding Ceph without ID being specified
    """
    serializer_class = ResourceSerializer

    def get(self, request: Request) -> Response:
        """
        summary: List Ceph devices

        description: |
            Retrieve a list of the Ceph devices that the requesting User owns.

        responses:
            200:
                description: A collection of Ceph records, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CephListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            search = controller.cleaned_data['search']
            if request.user.robot:
                search['project__region_id'] = request.user.address['id']
            elif request.user.id != 1:
                # A global-active user can list all Ceph drives for addresses in their member
                if request.user.is_global and request.user.global_active:
                    search['project__address_id__in'] = get_addresses_in_member(request, span)
                else:
                    search['project__address_id'] = request.user.address['id']

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = Resource.cephs.filter(
                    **search,
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_ceph_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'total_records': objs.count(),
                'warnings': controller.warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = ResourceSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Ceph entry

        description: Create a new Ceph entry using data given by user.

        responses:
            201:
                description: Ceph record was created successfully
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CephCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            # Remove the new boms, else they will be passed to the Resource constructor
            cd = controller.cleaned_data
            cd.update({
                'resource_type': resource_type.CEPH,
                'state': state.REQUESTED,
            })
            new_boms = cd.pop('new_boms', None)
            controller.instance.new_boms = new_boms
            controller.instance.save()

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            controller.instance.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ResourceSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CephResource(APIView):
    """
    Handles methods regarding Ceph that require an ID to be specified
    """
    serializer_class = ResourceSerializer

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a Ceph drive

        description: |
            Attempt to read information about a specific Ceph drive, returning 404 if Ceph drive doesn't exist or
            403 if user doesn't have permission.

        path_params:
            pk:
                description: The id of the Ceph drive to Read
                type: integer

        responses:
            200:
                description: Reads a Ceph drive
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Resource.objects.get(id=pk)
            except Resource.DoesNotExist:
                return Http404(error_code='iaas_ceph_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            obj.get_specs()
            data = ResourceSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Ceph drive

        description: |
            Attempt to update a Ceph drive by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the Ceph drive to be updated
                type: integer

        responses:
            200:
                description: Ceph drive was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Resource.objects.get(id=pk)
            except Resource.DoesNotExist:
                return Http404(error_code='iaas_ceph_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CephUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_robot_changes', child_of=request.span):
            cd = controller.cleaned_data
            if request.user.robot:
                # Robot should only be able to update state
                for key in cd.keys():
                    if key != 'state':
                        return Http403(error_code='iaas_ceph_update_002')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.new_boms = cd.get('new_boms')
            controller.instance.save()

        if not request.user.robot:
            with tracer.start_span('setting_run_robot_flags', child_of=request.span):
                controller.instance.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            # Get the most up-to-date specs
            if 'new_boms' in cd:
                controller.instance.refresh_from_db()
            data = ResourceSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Ceph drive
        """
        return self.put(request, pk, True)
