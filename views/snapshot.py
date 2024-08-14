"""
Management of Snapshots
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
from jaeger_client import Span
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import state as states
from iaas.models import (
    Snapshot,
    SnapshotHistory,
    VM,
)
from iaas.permissions.snapshot import Permissions
from iaas.controllers import SnapshotListController, SnapshotCreateController, SnapshotUpdateController
from iaas.serializers import SnapshotSerializer, SnapshotTreeSerializer
from iaas.utils import get_addresses_in_member


__all__ = [
    'SnapshotCollection',
    'SnapshotResource',
    'SnapshotTreeResource',
]


def get_active_in_subtree(snapshot: Snapshot, span: Span) -> Optional[str]:
    """
    Search a snapshot subtree recursively for an active snapshot. If the active snapshot is found
    then return that snapshot.
    """
    children = Snapshot.objects.filter(parent_id=snapshot.id).exclude(state=states.CLOSED)

    for child in children:
        if not child.active:
            return get_active_in_subtree(child, span)
        return child

    return None  # pragma: no cover


def update_snapshot_subtree(
    snapshot: Snapshot,
    new_state: int,
    user_id: int,
    is_head_of_tree: bool,
    span: Span,
) -> None:
    """
    Update children in a snapshot tree. Ignore the head of the tree.
    """
    if not is_head_of_tree:
        snapshot.state = new_state
        snapshot.modified_by = user_id
        snapshot.save()

        SnapshotHistory.objects.create(
            customer_address=snapshot.vm.project.address_id,
            modified_by=user_id,
            project_id=snapshot.vm.project.pk,
            snapshot=snapshot,
            state=new_state,
            vm_id=snapshot.vm.pk,
        )

    # children = Snapshot.objects.filter(parent_id=snapshot.id, vm=snapshot.vm.pk).exclude(state=states.CLOSED)
    for child in snapshot.children.iterator():
        update_snapshot_subtree(child, new_state, user_id, False, span)

    return None


class SnapshotCollection(APIView):
    """
    Handles methods regarding Snapshots that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List Snapshot records

        description: |
            Retrieve a list of the Snapshots.

        responses:
            200:
                description: A list of Snapshot records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SnapshotListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(vm__project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all snapshot records for customer_address in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(vm__project__address_id__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(vm__project__address_id=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):

            try:
                objs = Snapshot.objects.filter(
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
                return Http400(error_code='iaas_snapshot_list_001')

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
            data = SnapshotSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Snapshot

        description: Create a new Snapshot with data given by user

        responses:
            201:
                description: Snapshot record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SnapshotCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request, controller.instance.vm)
            if err is not None:
                return err

        with tracer.start_span('verify_snapshot_can_be_created', child_of=request.span):
            # A user can only change state if no snapshots are being scrubbed
            if Snapshot.objects.filter(
                vm_id=controller.instance.vm.pk,
            ).exclude(
                state__in=states.STABLE_STATES,
            ).exists():
                return Http400(error_code='iaas_snapshot_create_001')
            # A snapshot can only be created if the VM does not have GPUs attached
            if VM.objects.get(pk=controller.instance.vm.pk).gpu > 0:
                return Http400(error_code='iaas_snapshot_create_002')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.state = states.IN_API
            controller.instance.active = True
            controller.instance.save()

        with tracer.start_span('generate_snapshot_history', child_of=request.span):
            SnapshotHistory.objects.create(
                customer_address=controller.instance.vm.project.address_id,
                modified_by=request.user.id,
                project_id=controller.instance.vm.project.pk,
                snapshot=controller.instance,
                state=states.REQUESTED,
                vm_id=controller.instance.vm.pk,
            )

        with tracer.start_span('deactivate_parent_snapshot', child_of=request.span):
            if controller.cleaned_data['parent'] is not None:
                controller.cleaned_data['parent'].active = False
                controller.cleaned_data['parent'].save()
                controller.instance.refresh_from_db()

        with tracer.start_span('update_snapshot_state', child_of=request.span):
            controller.instance.state = states.REQUESTED
            controller.instance.save()

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            controller.instance.vm.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SnapshotSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class SnapshotResource(APIView):
    """
    Handles methods regarding Snapshot that do require a specific id
    """
    def head(self, request: Request, pk: int) -> Response:
        """
        summary: Verify a Snapshot record by the given `pk`.
        description: Verify if a Snapshot record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Snapshot.
                type: integer

        responses:
            200:
                description: Requested Snapshot exists and requesting User can access.
            404:
                description: Requesting user cannot access Snapshot if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Snapshot.objects.get(pk=pk)
            except Snapshot.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a Snapshot

        description: |
            Attempt to read information about a specific Snapshot, returning 404 if Snapshot doesn't exist or
            403 if user doesn't have permission.

        path_params:
            pk:
                description: The id of the Snapshot to Read
                type: integer

        responses:
            200:
                description: Reads a Snapshot
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Snapshot.objects.get(pk=pk)
            except Snapshot.DoesNotExist:
                return Http404(error_code='iaas_snapshot_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('fetching_email_addresses', child_of=request.span) as child_span:
            modified_by = SnapshotHistory.objects.filter(
                snapshot_id=obj.pk,
                state__in=states.SEND_EMAIL_STATES,
            ).order_by('-created')[0].modified_by
            manager_id = obj.vm.project.manager_id
            params = {'id__in': [modified_by, manager_id]}
            users = Membership.user.list(
                token=request.auth,
                params=params,
                span=child_span,
            ).json()['content']
            emails = []
            for user in users:
                emails.append(user['email'])
            obj.emails = emails

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SnapshotSerializer(instance=obj).data
        return Response({'content': data})

    def put(self, request: Request, pk: int) -> Response:
        """
        summary: Update the details of a specified Snapshot

        description: |
            Attempt to update a Snapshot by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the Snapshot to be updated
                type: integer

        responses:
            200:
                description: Snapshot was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Snapshot.objects.get(pk=pk)
            except Snapshot.DoesNotExist:
                return Http404(error_code='iaas_snapshot_update_001')

        with tracer.start_span('checking_if_snapshot_can_be_updated', child_of=request.span):
            # A user can only change state if no snapshots are being scrubbed
            if not self.request.user.robot and not obj.can_update():
                return Http400(error_code='iaas_snapshot_update_002')
            # A snapshot can only be updated if the VM does not have GPUs attached
            if obj.vm.gpu > 0:
                return Http400(error_code='iaas_snapshot_update_003')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SnapshotUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        if 'state' in controller.cleaned_data:
            # logic to change active snapshot
            if controller.cleaned_data['state'] == states.RUNNING_UPDATE:
                with tracer.start_span('change_current_active_status', child_of=request.span):
                    if not obj.active:
                        controller.instance.active = True
                        current_active_snapshots = Snapshot.objects.filter(
                            active=True,
                            vm_id=controller.instance.vm.id,
                        ).exclude(state=states.CLOSED).exclude(pk=controller.instance.id)

                        if current_active_snapshots.exists():
                            current_active_snapshot = current_active_snapshots[0]
                            current_active_snapshot.active = False
                            current_active_snapshot.save()

            # logic to remove snapshots
            if controller.cleaned_data['state'] == states.CLOSED:
                with tracer.start_span('closing_snapshot_update_tree', child_of=request.span) as span:
                    # meaning of terms used
                    # activate   -> set active = true
                    # deactivate -> set active = false

                    # deactivate snapshot before removal
                    activate_parent = False
                    with tracer.start_span('updating_active_snapshot', child_of=span) as child_span:
                        if not controller.instance.active:
                            current_active_snapshot = get_active_in_subtree(controller.instance, child_span)
                            if current_active_snapshot is not None:
                                current_active_snapshot.active = False
                                current_active_snapshot.save()
                                activate_parent = True
                        else:
                            controller.instance.active = False
                            activate_parent = True

                        if activate_parent and controller.instance.parent is not None:
                            # set parent as active
                            controller.instance.parent.active = True
                            controller.instance.parent.save()

                    with tracer.start_span('update_parent_in_subtree', child_of=span) as child_span:
                        if controller.instance.remove_subtree:
                            update_snapshot_subtree(
                                snapshot=controller.instance,
                                new_state=states.CLOSED,
                                user_id=request.user.id,
                                is_head_of_tree=True,
                                span=child_span,
                            )
                        else:
                            # parent gets new children
                            Snapshot.objects.filter(
                                parent_id=controller.instance.id,
                            ).exclude(
                                state=states.CLOSED,
                            ).update(
                                parent=controller.instance.parent,
                            )
            elif controller.cleaned_data['state'] == states.SCRUBBING:
                with tracer.start_span('scrubbing_snapshot_update_tree', child_of=request.span) as child_span:
                    if controller.instance.remove_subtree:
                        update_snapshot_subtree(
                            snapshot=controller.instance,
                            new_state=states.SCRUBBING,
                            user_id=request.user.id,
                            is_head_of_tree=True,
                            span=child_span,
                        )

            with tracer.start_span('generate_snapshot_history', child_of=request.span):
                SnapshotHistory.objects.create(
                    customer_address=obj.vm.project.address_id,
                    modified_by=request.user.id,
                    project_id=obj.vm.project.pk,
                    snapshot=obj,
                    state=controller.cleaned_data['state'],
                    vm_id=obj.vm.pk,
                )

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            obj.vm.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SnapshotSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk=int) -> Response:
        """
        Attempt to partially update a Snapshot
        """
        # put and patch provide same result for snapshots.
        # By including both services, a user can make a request using either put or patch
        # but the end result is the same
        return self.put(request, pk)


class SnapshotTreeResource(APIView):
    """
    Handles methods regarding Snapshot Tree that do require a specific id
    """

    def get(self, request: Request, vm_id: int) -> Response:
        """
        summary: Read a Snapshot Tree

        description: Return a Snapshot Tree for a specific VM.

        path_params:
            vm_id:
                description: The id of the VM to return the Snapshot Tree for.
                type: integer

        responses:
            200:
                description: Reads a Snapshot Tree for a VM
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                branches:
                                    description: A list of branches in the snapshot tree
                                    type: array
                                    items:
                                        description: Snapshot branch
                                        $ref: '#/components/schemas/SnapshotTree'
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validate_vm_id', child_of=request.span):
            try:
                obj = VM.objects.get(pk=vm_id)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_snapshot_tree_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.tree_read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('retrieving_snapshot_branches', child_of=request.span):
            branches = Snapshot.objects.filter(parent__isnull=True, vm_id=vm_id, state__lt=states.CLOSED)
        data = []
        with tracer.start_span('serializing_data', child_of=request.span):
            for branch in branches:
                data.append(SnapshotTreeSerializer(instance=branch).data)

        return Response({'content': {'branches': data}})
