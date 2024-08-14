# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas import skus, state as states
from iaas.models import Resource, Project


__all__ = [
    'CephCreateController',
    'CephListController',
    'CephUpdateController',
]


UPDATE_STATES = {states.RUNNING_UPDATE, states.QUIESCED_UPDATE}
VALID_NAME_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. '


class CephListController(ControllerBase):
    """
    Validates User data used to filter a list of Ceph drives
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'name',
        )
        search_fields = {
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'parent_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class CephCreateController(ControllerBase):
    """
    Validates Ceph data used to create a new Ceph record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Resource
        validation_order = (
            'project_id',
            'CEPH_001',
            'name',
        )

    def add_cleaned_bom(self, sku: str, quantity: int):
        if 'new_boms' not in self.cleaned_data:
            self.cleaned_data['new_boms'] = dict()
        self.cleaned_data['new_boms'][sku] = quantity

    def validate_project_id(self, project_id: Optional[int]) -> Optional[str]:
        """
        description: The id of a valid project in the User's Address
        type: integer
        """
        if project_id is None:
            return 'iaas_ceph_create_101'
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            return 'iaas_ceph_create_102'

        try:
            project = Project.objects.get(
                id=project_id,
                address_id=self.request.user.address_id,
                closed=False,
            )
        except Project.DoesNotExist:
            return 'iaas_ceph_create_103'

        self.cleaned_data['project'] = project
        return None

    def validate_CEPH_001(self, ceph_001: Optional[int]) -> Optional[str]:  # noqa: N802
        """
        description: The size of the Ceph block device, in GB
        type: integer
        """
        if ceph_001 is None:
            return 'iaas_ceph_create_104'

        try:
            ceph_001 = int(ceph_001)
        except (TypeError, ValueError):
            return 'iaas_ceph_create_105'

        if ceph_001 <= 0:
            return 'iaas_ceph_create_106'

        self.add_cleaned_bom(skus.CEPH_001, ceph_001)
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The user-friendly name for the ceph block device
        type: integer
        """
        if name is None:
            name = ''

        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_ceph_create_107'

        for char in name:
            if char not in VALID_NAME_CHARS:
                return 'iaas_ceph_create_108'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_ceph_create_109'

        project = self.cleaned_data.get('project')
        if project is None:
            return None

        # The name must be unique within all an address' projects in a region
        duplicate_ceph_name = Resource.cephs.filter(
            project__address_id=project.address_id,
            project__region_id=project.region_id,
            state__lt=states.CLOSED,
            name=name,
        )
        if duplicate_ceph_name.exists():
            return 'iaas_ceph_create_110'

        self.cleaned_data['name'] = name
        return None


class CephUpdateController(ControllerBase):
    """
    Validates Ceph data used to update a Ceph record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Resource
        validation_order = (
            'state',
            'CEPH_001',
            'name',
        )

    def add_cleaned_bom(self, sku: str, quantity: int):
        if 'new_boms' not in self.cleaned_data:
            self.cleaned_data['new_boms'] = dict()
        self.cleaned_data['new_boms'][sku] = quantity

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: The state that the Ceph drive should be put into
        type: integer
        """
        if state is None:
            return None

        try:
            state = int(state)
        except (TypeError, ValueError):
            return 'iaas_ceph_update_101'

        if state == self._instance.state:
            return None

        # Find out what the valid state changes are
        if self.request.user.robot:
            state_map = states.ROBOT_STATE_MAP
        else:
            state_map = states.USER_STATE_MAP

        # Ensure the current state is in the map
        current_state = self._instance.state
        if current_state not in state_map:
            return 'iaas_ceph_update_102'

        # Ensure the requested end-state is a valid state change
        if state not in state_map[current_state]:
            return 'iaas_ceph_update_103'

        self.cleaned_data['state'] = state
        return None

    def validate_CEPH_001(self, ceph_001: Optional[int]) -> Optional[str]:  # noqa: N802
        """
        description: The size of the Ceph block device, in GB
        type: integer
        """
        if ceph_001 is None:
            return 'iaas_ceph_update_104'

        try:
            ceph_001 = int(ceph_001)
        except (TypeError, ValueError):
            return 'iaas_ceph_update_105'

        current_capacity = self._instance.get_current_quantity(skus.CEPH_001)
        if ceph_001 == current_capacity:
            return None

        # Cannot decrease the size of a Ceph drive
        if ceph_001 < current_capacity:
            return 'iaas_ceph_update_106'

        if 'state' not in self.cleaned_data:
            if self._instance.state == states.RUNNING:
                self.cleaned_data['state'] = states.RUNNING_UPDATE
            elif self._instance.state == states.QUIESCED:
                self.cleaned_data['state'] = states.QUIESCED_UPDATE
            else:
                return 'iaas_ceph_update_107'
        else:
            # Check that the requested state change will be running / quiesced update states
            if self.cleaned_data['state'] not in UPDATE_STATES:
                return 'iaas_ceph_update_108'

        self.add_cleaned_bom(skus.CEPH_001, ceph_001)
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The user-friendly name for the Ceph block device
        type: integer
        """
        if name is None:
            name = ''

        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_ceph_update_109'

        for char in name:
            if char not in VALID_NAME_CHARS:
                return 'iaas_ceph_update_110'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_ceph_update_111'

        project = self.cleaned_data.get('project', self._instance.project)

        # The name must be unique within all an Address' Projects in a Region
        duplicate_ceph_name = Resource.cephs.filter(
            project__address_id=project.address_id,
            project__region_id=project.region_id,
            state__lt=states.CLOSED,
            name=name,
        ).exclude(
            pk=self._instance.pk,
        )
        if duplicate_ceph_name.exists():
            return 'iaas_ceph_update_112'

        self.cleaned_data['name'] = name
        return None
