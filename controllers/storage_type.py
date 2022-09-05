# stdlib
from typing import List, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import StorageType

__all__ = [
    'StorageTypeListController',
    'StorageTypeUpdateController',
]


class StorageTypeListController(ControllerBase):
    """
    Lists the storage types.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase meta to make it more specific
        to the StorageTypeList.
        """
        allowed_ordering = (
            'id',
        )
        search_fields = {
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'regions__region': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class StorageTypeUpdateController(ControllerBase):
    """
    Validates storage type data used to update an storage type.
    """
    _instance: StorageType

    class Meta(ControllerBase.Meta):
        """
        Assign the model and validation order for fields.
        """
        model = StorageType
        validation_order = (
            'regions',
        )

    def validate_regions(self, regions: Optional[List[int]]) -> Optional[str]:
        """
        description: Ensures that the regions sent are valid.
        type: array
        items:
            type: integer
        """
        # Ensure the value sent is a list.
        regions = regions or []
        if not isinstance(regions, list):
            return 'iaas_storage_type_update_101'

        if len(regions) == 0:
            return 'iaas_storage_type_update_102'

        # Check if all sent values are integers.
        try:
            regions_set = {int(region) for region in regions}
        except (TypeError, ValueError):
            return 'iaas_storage_type_update_103'

        # Verify the addresses are all cloud_regions
        regions = list(regions_set)
        response = Membership.address.list(
            token=self.request.auth,
            params={'search[id__in]': regions},
            span=self.span,
        )

        if response.status_code != 200:
            return 'iaas_storage_type_update_104'  # pragma: no cover

        if len(response.json()['content']) != len(regions):
            return 'iaas_storage_type_update_105'

        if not all([address['cloud_region'] for address in response.json()['content']]):
            return 'iaas_storage_type_update_106'

        self.cleaned_data['regions'] = regions
        return None
