# stdlib
from typing import cast, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas import state as states
from iaas.models import Snapshot, VM


__all__ = [
    'SnapshotCreateController',
    'SnapshotListController',
    'SnapshotUpdateController',
]


class SnapshotListController(ControllerBase):
    """
    Validates User data used to filter a list of Snapshots
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'id',
            'name',
            'active',
            'created',
            'parent_id',
            'state',
            'vm_id',
        )
        search_fields = {
            'active': (),
            'created': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'parent_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'remove_subtree': (),
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__server_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class SnapshotCreateController(ControllerBase):
    """
    Validates User data used to create a Snapshot
    """

    class Meta(ControllerBase.Meta):
        """
        Override ControllerBase.Meta fields
        """
        model = Snapshot
        validation_order = (
            'vm_id',
            'name',
        )

    def validate_vm_id(self, vm_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the VM for which a snapshot should be created.
        type: integer
        """
        # vm_id is sent
        try:
            vm_id = int(cast(int, vm_id))
        except (TypeError, ValueError):
            return 'iaas_snapshot_create_101'

        # check valid vm record
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return 'iaas_snapshot_create_102'

        # Check that vm is in correct state for creation of snapshot
        if vm.state != states.RUNNING:
            return 'iaas_snapshot_create_103'

        # check
        parent = None
        current_active_snapshots = Snapshot.objects.filter(vm_id=vm_id, active=True).exclude(state=states.CLOSED)

        if current_active_snapshots.exists():
            # only expect 1 snapshot with active = True
            if len(current_active_snapshots) > 1:
                return 'iaas_snapshot_create_104'

            # current active snapshot must be in state RUNNING
            if current_active_snapshots[0].state != states.RUNNING:
                return 'iaas_snapshot_create_105'
            parent = current_active_snapshots[0]

        self.cleaned_data['vm'] = vm
        self.cleaned_data['parent'] = parent
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name to be given to the new Snapshot
        type: string
        """
        # name is sent
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_snapshot_create_106'

        if 'vm' not in self.cleaned_data:
            return None

        vm = self.cleaned_data['vm']

        # check name unique for snapshot
        if Snapshot.objects.filter(name=name, vm=vm).exclude(state=states.CLOSED).exists():
            return 'iaas_snapshot_create_107'
        self.cleaned_data['name'] = name
        return None


class SnapshotUpdateController(ControllerBase):
    """
    Validates Snapshot data used to update a Snapshot
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = Snapshot
        validation_order = (
            'name',
            'state',
            'remove_subtree',
        )

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: A name for the snapshot. Must be unique for a vm.
        type: string
        required: false
        """
        if name is None:
            return None
        name = str(name).strip()

        if len(name) == 0:
            return None

        if len(name) > self.get_field('name').max_length:
            return 'iaas_snapshot_update_101'

        if Snapshot.objects.filter(
            vm_id=self._instance.vm.id,
            name=name,
        ).exclude(pk=self._instance.pk).exclude(state=states.CLOSED).exists():
            return 'iaas_snapshot_update_102'

        self.cleaned_data['name'] = name
        return None

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: The new state for the snapshot
        type: integer
        required: false
        """
        if state is None:
            return None

        try:
            state = int(cast(int, state))
        except (ValueError, TypeError):
            return 'iaas_snapshot_update_103'

        # Ignore if we're not changing the state
        if state == self._instance.state:
            return None

        # Ensure the sent state is in the valid range
        if state not in states.VALID_RANGE:
            return 'iaas_snapshot_update_104'

        # Determine which state map to use for this request
        if self.request.user.robot:
            available_states = states.ROBOT_STATE_MAP
        else:
            available_states = states.USER_SNAPSHOT_STATE_MAP

        # Ensure current state is in chosen map.
        if self._instance.state not in available_states:
            return 'iaas_snapshot_update_105'

        # Ensure sent state is a valid state change.
        if state not in available_states[self._instance.state]:
            return 'iaas_snapshot_update_106'

        # Can only change state if VM has state RUNNING
        if self._instance.vm.state != states.RUNNING:
            return 'iaas_snapshot_update_107'

        self.cleaned_data['state'] = state
        return None

    def validate_remove_subtree(self, remove_subtree: Optional[bool]) -> Optional[str]:
        """
        description: Describes if removing a snapshot should also remove the snapshot subtree
        type: bool
        required: false
        """
        # default is False
        if remove_subtree is None:
            return None

        if not isinstance(remove_subtree, bool):
            return 'iaas_snapshot_update_108'

        if not remove_subtree:
            return None

        if 'state' not in self.cleaned_data:
            return 'iaas_snapshot_update_109'

        if self.cleaned_data['state'] != states.SCRUB:
            return 'iaas_snapshot_update_110'

        self.cleaned_data['remove_subtree'] = remove_subtree
        return None
