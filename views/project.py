"""
Views for Project
"""
# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import Project, VMHistory
from iaas.permissions.project import Permissions
from iaas.controllers import (
    ProjectListController,
    ProjectCreateController,
    ProjectUpdateController,
)
from iaas.serializers import ProjectSerializer
import iaas.state as states
from iaas.utils import get_addresses_in_member


__all__ = [
    'ProjectCollection',
    'ProjectResource',
]


class ProjectCollection(APIView):
    """
    Handles methods regarding Project that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List Projects

        description: |
            Attempt to list Projects

        responses:
            200:
                description: A list of Project records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ProjectListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all projects in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(address_id__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(address_id=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = Project.objects.filter(
                    **controller.cleaned_data['search'],
                )

                if address_filtering:
                    objs = objs.filter(address_filtering)

                objs = objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (TypeError, ValueError, ValidationError):
                return Http400(error_code='iaas_project_list_001')

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
            data = ProjectSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create Projects

        description: |
            Attempt to Create Projects

        responses:
            201:
                description: Projects where created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ProjectCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('controller.save', child_of=request.span) as span:
            errors = controller.save(span)
            if errors is not None:
                return Http400(**errors)

        with tracer.start_span('set_virtual_router_to_requested', child_of=span):
            virtual_router = controller.instance.virtual_router
            virtual_router.state = states.REQUESTED
            virtual_router.save()

        with tracer.start_span('saving_and_setting_run_robot_flags', child_of=span):
            # `set_run_robot_flags` calls .save()
            controller.instance.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ProjectSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class ProjectResource(APIView):
    """
    Handles methods regarding Project that do require a specific id
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Project record by the given `pk`.
        description: Verify if a Project record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Project.
                type: integer

        responses:
            200:
                description: Requested Project exists and requesting User can access.
            404:
                description: Requesting user cannot access Project if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a Project

        description: |
            Attempt to read information about a specific Project, returning 404 if Project doesn't exist or
            403 if user doesn't hav permission.

        path_params:
            pk:
                description: The id of the Project to Read
                type: integer

        responses:
            200:
                description: Reads a Project
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_project_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ProjectSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update a Project

        description: |
            Attempt to Update a Project using the data supplied by the User.

        path_params:
            pk:
                description: The ID of the Project to Update
                type: integer

        responses:
            201:
                description: Project was Updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_project_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = ProjectUpdateController(
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

        with tracer.start_span('changing_infrastructure_states', child_of=request.span):

            state = controller.cleaned_data.pop('state', None)

            if state == 4:
                obj.virtual_router.state = 7
                obj.virtual_router.save()
                for vm in obj.vms.exclude(state=states.CLOSED):
                    # Fetch the last stable state from VMHistory logs before scrub was requested for VMs that are not
                    # closed
                    stable_state = VMHistory.objects.filter(
                        vm=vm,
                        state__in=states.VM_RESTORE_STATES,
                    ).values_list('state', flat=True).order_by('-created').first()
                    # From last stable state find what state VM should be restored to, quiesced is the default
                    new_state = states.VM_RESTORE_MAP.get(stable_state, states.QUIESCED)
                    VMHistory.objects.create(
                        vm=vm,
                        modified_by=request.user.id,
                        customer_address=controller.instance.address_id,
                        project_id=controller.instance.pk,
                        project_vm_name=f'{controller.instance.name}_{vm.name}',
                        state=new_state,
                    )
                    vm.state = new_state
                    vm.save()
                controller.instance.set_run_robot_flags()
            elif state == 8:
                obj.virtual_router.state = 8
                obj.virtual_router.save()
                for vm in obj.vms.exclude(state=states.CLOSED):
                    VMHistory.objects.create(
                        vm=vm,
                        modified_by=request.user.id,
                        customer_address=controller.instance.address_id,
                        project_id=controller.instance.pk,
                        project_vm_name=f'{controller.instance.name}_{vm.name}',
                        state=8,
                    )
                    vm.state = 8
                    vm.save()
                controller.instance.set_run_robot_flags()
            else:
                # Robot Flags and cache does not need to be set, saving other changes to instance
                controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = ProjectSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update Project
        """
        return self.put(request, pk, True)
