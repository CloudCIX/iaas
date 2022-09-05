# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Storage

__all__ = [
    'StorageListController',
    'StorageCreateController',
    'StorageUpdateController',
]

VALID_RANGE = range(10, 10001)


class StorageListController(ControllerBase):
    """
    Validates user data used to filter a list of storage devices in a vm
    """
    class Meta(ControllerBase.Meta):
        allowed_ordering = (
            'gb',
            'name',
            'primary',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'primary': (),
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class StorageCreateController(ControllerBase):
    """
    Validates user data used to create a new storage device record
    """

    class Meta(ControllerBase.Meta):
        model = Storage
        validation_order = (
            'gb',
            'name',
            'primary',
        )

    def validate_gb(self, gb: Optional[int]) -> Optional[str]:
        """
        description: The size in GB of the Storage drive.
        type: integer
        """
        if gb is None:
            return 'iaas_storage_create_101'

        try:
            gb = int(gb)
        except (TypeError, ValueError):
            return 'iaas_storage_create_102'

        if gb not in VALID_RANGE:
            return 'iaas_storage_create_103'

        self.cleaned_data['gb'] = gb
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            The verbose name of the Storage drive.

            Note that this name is used only within the CloudCIX API, and is not the name that will be used on the
            underlying hardware when the VM is built.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_storage_create_104'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_storage_create_105'

        self.cleaned_data['name'] = name
        return None

    def validate_primary(self, primary: Optional[bool]) -> Optional[str]:
        """
        description: |
            A flag determining whether or not this Storage object is the primary drive for the VM.

            VMs can only have one primary drive each.
        type: boolean
        """
        if primary is None:
            primary = False

        if primary not in {True, False}:
            return 'iaas_storage_create_106'

        self.cleaned_data['primary'] = primary
        return None


class StorageUpdateController(ControllerBase):
    """
    Validates user data used to update storage device record
    """
    capacity_change = 0

    class Meta(ControllerBase.Meta):
        model = Storage
        validation_order = (
            'gb',
            'name',
        )

    def validate_gb(self, gb: Optional[int]) -> Optional[str]:
        """
        description: |
            The size in GB of the Storage drive.
            The size of the drive cannot be reduced, only increased.
        type: integer
        """
        if gb is None or gb == self._instance.gb:
            return None

        try:
            gb = int(gb)
        except (TypeError, ValueError):
            return 'iaas_storage_update_101'

        if gb not in VALID_RANGE:
            return 'iaas_storage_update_102'

        # Check against instance data here, return same error code
        if gb < self._instance.gb:
            return 'iaas_storage_update_102'

        self.capacity_change = gb - self._instance.gb

        self.cleaned_data['gb'] = gb
        self.cleaned_data['update_history'] = True

        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The verbose name of the Storage drive.
        type: string
        """
        if name is None or name == self._instance.name:
            return None
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_storage_update_103'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_storage_update_104'

        self.cleaned_data['name'] = name
        return None
