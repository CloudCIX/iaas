# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Image, RegionImage

__all__ = [
    'RegionImageCreateController',
]


class RegionImageCreateController(ControllerBase):
    """
    Validates RegionImage data used to create a new RegionImage record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = RegionImage
        validation_order = (
            'image_id',
        )

    def validate_image_id(self, image_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Image that the RegionImage is being allocated to.
        type: integer
        """
        if image_id is None:
            return 'iaas_region_image_create_101'

        # Try and fetch the Image object.
        try:
            image_id = int(image_id)
            image = Image.objects.get(id=image_id)
        except (TypeError, ValueError):
            return 'iaas_region_image_create_102'
        except Image.DoesNotExist:
            return 'iaas_region_image_create_103'

        # Ensure RegionImage record does not already exist for user address:
        if RegionImage.objects.filter(image_id=image_id, region=self.request.user.address['id']).exists():
            return 'iaas_region_image_create_104'

        self.cleaned_data['image'] = image
        return None
