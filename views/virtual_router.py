"""
Management of VirtualRouters
"""
# stdlib
from typing import List, Optional
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import state
from iaas.controllers import VirtualRouterListController, VirtualRouterUpdateController
from iaas.controllers.helpers import create_cloud_subnets, IAASException
from iaas.models import Project, Subnet, VirtualRouter
from iaas.permissions.virtual_router import Permissions
from iaas.serializers import VirtualRouterSerializer
from iaas.utils import get_addresses_in_member


__all__ = [
    'VirtualRouterCollection',
    'VirtualRouterResource',
]


class VirtualRouterCollection(APIView):
    """
    Returns a list of the virtual routers.
    """

    def get(self, request: Request) -> Response:
        """
        summary: List VirtualRouter records

        description: |
            Retrieve a list of VirtualRouter records. Each Project has one VirtualRouter associated with it, that
            handles all of the networking and Firewall capabilities for the Project.

        responses:
            200:
                description: A list of VirtualRouter records
            400: {}
        """

        tracer = settings.TRACER

        # Retrieve and validate the controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VirtualRouterListController(
                data=request.GET,
                request=request,
                span=span,
            )
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all virtual routers for addresses in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(project__address_id__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(project__address_id=request.user.address['id'])

        # Fetch items.
        with tracer.start_span('retrieving_objects', child_of=request.span):
            try:
                objs = VirtualRouter.objects.filter(
                    **controller.cleaned_data['search'],
                )

                if address_filtering:
                    objs = objs.filter(address_filtering)

                objs = objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_virtual_router_list_001')

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
            data = VirtualRouterSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class VirtualRouterResource(APIView):
    """
    Return an individual VirtualRouter object.
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Virtual Router record by the given `pk`.
        description: |
            Verify if a Virtual Router record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Virtual Router.
                type: integer

        responses:
            200:
                description: Requested Virtual Router exists and requesting User can access.
            404:
                description: Requesting user cannot access Virtual Router if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VirtualRouter.objects.get(pk=pk)
            except VirtualRouter.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.head(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Retrieve details of a specific VirtualRouter.

        description: Retrieve the details of the VirtualRouter with id 'pk'.

        path_params:
            pk:
                description: The ID of the VirtualRouter to be retrieved.
                type: integer

        responses:
            200:
                description: A VirtualRouter is returned
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = VirtualRouter.objects.get(pk=pk)
            except VirtualRouter.DoesNotExist:
                return Http404(error_code='iaas_virtual_router_read_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return error

        # Serialise the data and return.
        with tracer.start_span('serializing_data', child_of=request.span):
            data = VirtualRouterSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified VirtualRouter.

        description: Attempt to update an VirtualRouter record by the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The id of the VirtualRouter to be updated.
                type: integer

        responses:
            200:
                description: VirtualRouter was updated successfully.
            400: {}
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = VirtualRouter.objects.get(pk=pk)
            except VirtualRouter.DoesNotExist:
                return Http404(error_code='iaas_virtual_router_update_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.update(request, obj)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as child_span:
            controller = VirtualRouterUpdateController(
                data=request.data,
                request=request,
                partial=partial,
                span=child_span,
                instance=obj,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_virtual_router_subnets', child_of=request.span) as span:
            subnets = controller.cleaned_data.pop('subnets', {})

            new_subs: List[Subnet] = []
            for sub in subnets:
                if not sub.pk:
                    new_subs.append(sub)
                else:
                    sub.save()

            if len(new_subs) > 0:
                try:
                    create_cloud_subnets(
                        self.request,
                        obj.project,
                        new_subs,
                        'iaas_virtual_router_update_002',
                        span=span,
                    )
                except IAASException as e:
                    return Http400(error_code=e.args[0])

        with tracer.start_span('scrubbing_object', child_of=request.span):
            if controller.scrub_virtual_router:
                if obj.project.vms.exclude(state=state.CLOSED).exists():
                    return Http400(error_code='iaas_virtual_router_update_003')

        # Save objects.
        with tracer.start_span('saving_objects', child_of=request.span) as span:
            if controller.update_virtual_router and controller.instance.can_update():
                if obj.state == state.RUNNING:
                    controller.instance.state = state.RUNNING_UPDATE
                elif obj.state == state.QUIESCED:
                    controller.instance.state = state.QUIESCED_UPDATE
            controller.instance.save()

        if controller.close_virtual_router:
            with tracer.start_span('closing_object', child_of=request.span):
                obj.set_deleted()
                Project.objects.filter(pk=obj.project.pk).update(run_icarus=True)

        if not request.user.robot or controller.scrub_virtual_router:
            with tracer.start_span('activate_run_robot_and_run_icarus', child_of=request.span):
                Project.objects.filter(pk=obj.project.pk).update(run_robot=True, run_icarus=True)

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = VirtualRouterSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update an VirtualRouter.
        """
        return self.put(request, pk, True)
