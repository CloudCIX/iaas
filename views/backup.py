"""
Management of Backups
"""
# stdlib
from typing import Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import state as states
from iaas.controllers import BackupListController, BackupCreateController, BackupUpdateController
from iaas.models import (
    Backup,
    BackupHistory,
    VM,
)
from iaas.permissions.backup import Permissions
from iaas.serializers import BackupSerializer
from iaas.utils import get_addresses_in_member


__all__ = [
    'BackupCollection',
    'BackupResource',
]


class BackupCollection(APIView):
    """
    Handles methods regarding Backups that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List Backup records

        description: |
            Retrieve a list of Backups.

        responses:
            200:
                description: A list of Backup records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = BackupListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(vm__project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all backups in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(vm__project__address_id__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(vm__project__address_id=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = Backup.objects.filter(
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
                return Http400(error_code='iaas_backup_list_001')

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
            data = BackupSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Backup

        description: Create a new Backup with data given by user

        responses:
            201:
                description: Backup record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = BackupCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request, controller.instance.vm)
            if err is not None:
                return err

        with tracer.start_span('verify_backup_can_be_created', child_of=request.span):
            # A backup can only be created if no backups are being scrubbed
            if Backup.objects.filter(
                vm_id=controller.instance.vm.pk,
            ).exclude(
                state__in=states.STABLE_STATES,
            ).exists():
                return Http400(error_code='iaas_backup_create_001')
            # A backup can only be created if the VM does not have GPUs attached
            if VM.objects.get(pk=controller.instance.vm.pk).gpu > 0:
                return Http400(error_code='iaas_backup_create_002')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.state = states.REQUESTED
            controller.instance.save()

        with tracer.start_span('generate_backup_history', child_of=request.span):
            BackupHistory.objects.create(
                backup=controller.instance,
                customer_address=request.user.address['id'],
                modified_by=request.user.id,
                project_id=controller.instance.vm.project.pk,
                state=states.REQUESTED,
                vm_id=controller.instance.vm.pk,
            )

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            controller.instance.vm.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = BackupSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class BackupResource(APIView):
    """
    Handles methods regarding Backups that do require a specific id
    """
    def head(self, request: Request, pk: int) -> Response:
        """
        summary: Verify a Backup record by the given `pk`.
        description: Verify if a Backup record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Backup.
                type: integer

        responses:
            200:
                description: Requested Backup exists and requesting User can access.
            404:
                description: Requesting user cannot access Backup if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Backup.objects.get(pk=pk)
            except Backup.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a Backup

        description: |
            Attempt to read information about a specific Backup, returning 404 if Backup doesn't exist or
            403 if user doesn't have permission.

        path_params:
            pk:
                description: The id of the Backup to Read
                type: integer

        responses:
            200:
                description: Reads a Backup
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Backup.objects.get(pk=pk)
            except Backup.DoesNotExist:
                return Http404(error_code='iaas_backup_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('fetching_email_addresses', child_of=request.span) as child_span:
            modified_by = BackupHistory.objects.filter(
                backup_id=obj.pk,
                state__in=states.SEND_EMAIL_STATES,
            ).order_by('-created')[0].modified_by
            manager_id = obj.vm.project.manager_id
            params = {'id__in': [modified_by, manager_id]}
            users = Membership.user.list(token=request.auth, params=params, span=child_span).json()['content']
            emails = []
            for user in users:
                emails.append(user['email'])
            obj.emails = emails

        with tracer.start_span('serializing_data', child_of=request.span):
            data = BackupSerializer(instance=obj).data
        return Response({'content': data})

    def put(self, request: Request, pk: int) -> Response:
        """
        summary: Update the details of a specified Backup

        description: |
            Attempt to update a Backup by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the Backup to be updated
                type: integer

        responses:
            200:
                description: Backup was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Backup.objects.get(pk=pk)
            except Backup.DoesNotExist:
                return Http404(error_code='iaas_backup_update_001')

        with tracer.start_span('checking_if_backup_can_be_updated', child_of=request.span):
            # A user can only change state if no backups are being scrubbed
            if not self.request.user.robot and not obj.can_update():
                return Http400(error_code='iaas_backup_update_002')

        current_time_valid = obj.time_valid

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = BackupUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj, current_time_valid, controller.instance.time_valid)
            if err is not None:
                return err

        if 'state' in controller.cleaned_data:
            with tracer.start_span('generate_backup_history', child_of=request.span):
                BackupHistory.objects.create(
                    backup=obj,
                    customer_address=request.user.address['id'],
                    modified_by=request.user.id,
                    project_id=controller.instance.vm.project.pk,
                    state=controller.cleaned_data['state'],
                    vm_id=controller.instance.vm.pk,
                )

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            obj.vm.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = BackupSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk=int) -> Response:
        """
        Attempt to partially update a Backup
        """
        # put and patch provide same result for Backups
        # By including both services, a user can make a request using either put or patch
        # but the end result is the same
        return self.put(request, pk)
