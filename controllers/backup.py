# stdlib
from typing import cast, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from datetime import datetime
# local
from iaas import state as states
from iaas.models import Backup, VM

__all__ = [
    'BackupCreateController',
    'BackupListController',
    'BackupUpdateController',
]


class BackupListController(ControllerBase):
    """
    Validates User data used to filter a list of Backups
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'time_valid',
            'created',
            'name',
            'id',
            'name',
            'state',
            'vm_id',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'timestamp': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vm__project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm__server_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class BackupCreateController(ControllerBase):
    """
    Validates User data used to create a Backup
    """

    class Meta(ControllerBase.Meta):
        """
        Override ControllerBase.Meta fields
        """
        model = Backup
        validation_order = (
            'vm_id',
            'name',
            'repository',
        )

    def validate_vm_id(self, vm_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the VM for which a backup should be created.
        type: integer
        """
        # vm_id is sent
        try:
            vm_id = int(cast(int, vm_id))
        except (TypeError, ValueError):
            return 'iaas_backup_create_101'

        # check valid vm record
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return 'iaas_backup_create_102'

        # Check that vm is in correct state for creation of backup
        valid_states = [states.RUNNING, states.QUIESCED]
        if vm.state not in valid_states:
            return 'iaas_backup_create_103'

        self.cleaned_data['vm'] = vm
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name to be given to the new Backup
        type: string
        """
        # name is sent
        if not bool(name):
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_backup_create_104'

        if 'vm' not in self.cleaned_data:
            return None

        vm = self.cleaned_data['vm']

        # check name unique for backup
        if Backup.objects.filter(name=name, vm=vm).exclude(state=states.CLOSED).exists():
            return 'iaas_backup_create_105'
        self.cleaned_data['name'] = name
        return None

    def validate_repository(self, repository: Optional[int]) -> Optional[str]:
        """
        description: |
            This i sthe backup location, with the primary backup being repository = 1 and secondary backup being
            repository = 2.
        type: integer
        """
        try:
            repository = int(cast(int, repository))
        except (TypeError, ValueError):
            return 'iaas_backup_create_106'

        if repository not in range(1, 3):
            return 'iaas_backup_create_107'

        self.cleaned_data['repository'] = repository
        return None


class BackupUpdateController(ControllerBase):
    """
    Validates Backup data used to update a Backup
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = Backup
        validation_order = (
            'name',
            'state',
            'time_valid',
        )

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: A name for the backup. Must be unique for a vm.
        type: string
        required: false
        """
        if name is None:
            return None
        name = str(name).strip()

        if len(name) == 0:
            return None

        if len(name) > self.get_field('name').max_length:
            return 'iaas_backup_update_101'

        if Backup.objects.filter(
            vm_id=self._instance.vm.id,
            name=name,
        ).exclude(pk=self._instance.pk).exclude(state=states.CLOSED).exists():
            return 'iaas_backup_update_102'

        self.cleaned_data['name'] = name
        return None

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: The new state for the backup
        type: integer
        required: false
        """
        if state is None:
            return None

        try:
            state = int(cast(int, state))
        except (ValueError, TypeError):
            return 'iaas_backup_update_103'

        # Ignore if we're not changing the state
        if state == self._instance.state:
            return None

        # Ensure the sent state is in the valid range
        if state not in states.VALID_RANGE:
            return 'iaas_backup_update_104'

        # Determine which state map to use for this request
        if self.request.user.robot:
            available_states = states.ROBOT_STATE_MAP
        else:
            available_states = states.USER_BACKUP_STATE_MAP

        # Ensure current state is in chosen map.
        if self._instance.state not in available_states:
            return 'iaas_backup_update_105'

        # Ensure sent state is a valid state change.
        if state not in available_states[self._instance.state]:
            return 'iaas_backup_update_106'

        # Can only change state if VM has state RUNNING or QUIESCED
        if self._instance.vm.state not in [states.RUNNING, states.QUIESCED]:
            return 'iaas_backup_update_107'

        self.cleaned_data['state'] = state
        return None

    def validate_time_valid(self, time_valid: Optional[str]) -> Optional[str]:
        """
        description: Date and time the backup is valid from
        type: string
        """
        if time_valid is None:
            return None

        try:
            formatted_time_valid = datetime.strptime(str(time_valid), '%Y-%m-%d  %H:%M:%S')
        except (TypeError, ValueError):
            return 'iaas_backup_update_108'

        self.cleaned_data['time_valid'] = formatted_time_valid
        return None
