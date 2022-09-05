# stdlib
import logging
from typing import List, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Image

__all__ = [
    'ImageListController',
    'ImageUpdateController',
]


class ImageListController(ControllerBase):
    """
    Lists the images for VMs.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase meta to make it more specific
        to the ImageList.
        """
        allowed_ordering = (
            'display_name',
            'id',
        )
        search_fields = {
            'display_name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'regions__region': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class ImageUpdateController(ControllerBase):
    """
    Validates image data used to update an image.
    """
    logger = logging.getLogger('iaas.controllers.image.update')

    class Meta(ControllerBase.Meta):
        """
        Assign the model and validation order for fields.
        """
        model = Image
        validation_order = (
            'regions',
        )

    def validate_regions(self, regions: Optional[List[int]]) -> Optional[str]:
        """
        description: |
            An array of IDs of region Addresses that correspond with the cloud regions that the Image is supported in.
        type: array
        items:
            type: integer
        """

        # Ensure the value sent is a list.
        regions = regions or []
        if not isinstance(regions, list):
            return 'iaas_image_update_101'

        if len(regions) == 0:
            return 'iaas_image_update_102'

        # Check if all sent values are integers.
        try:
            regions_set = {int(region) for region in regions}
        except (TypeError, ValueError):
            return 'iaas_image_update_103'

        # Verify the addresses are all cloud_regions
        regions = list(regions_set)
        response = Membership.address.list(
            token=self.request.auth,
            params={'search[id__in]': regions},
            span=self.span,
        )

        if response.status_code != 200:  # pragma: no cover
            self.logger.error(
                f'Error validating the regions list against the Membership API: {response.content.decode()}',
            )
            return 'iaas_image_update_104'

        if len(response.json()['content']) != len(regions):
            return 'iaas_image_update_105'

        if not all([address['cloud_region'] for address in response.json()['content']]):
            return 'iaas_image_update_106'

        self.cleaned_data['regions'] = regions
        return None
