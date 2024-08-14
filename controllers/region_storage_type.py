# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import RegionStorageType, StorageType

__all__ = [
    'RegionStorageTypeCreateController',
]


class RegionStorageTypeCreateController(ControllerBase):
    """
    Validates RegionStorageType data used to create a new RegionStorageType record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = RegionStorageType
        validation_order = (
            'storage_type_id',
        )

    def validate_storage_type_id(self, storage_type_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Storage Type that the RegionStorageType is being allocated to.
        type: integer
        """
        if storage_type_id is None:
            return 'iaas_region_storage_type_create_101'

        # Try and fetch the storage_type object.
        try:
            storage_type_id = int(storage_type_id)
            storage_type = StorageType.objects.get(id=storage_type_id)
        except (TypeError, ValueError):
            return 'iaas_region_storage_type_create_102'
        except StorageType.DoesNotExist:
            return 'iaas_region_storage_type_create_103'

        # Ensure RegionStorageType record does not already exist for user address:
        if RegionStorageType.objects.filter(
            storage_type_id=storage_type_id,
            region=self.request.user.address['id'],
        ).exists():
            return 'iaas_region_storage_type_create_104'

        self.cleaned_data['storage_type'] = storage_type
        return None
