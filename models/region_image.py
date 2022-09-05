# libs
from django.db import models
from django.urls import reverse
# local
from .image import Image

__all__ = [
    'RegionImage',
]


class RegionImage(models.Model):
    """
    A table for handling relationships between Images and Regions.
    """
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='regions')
    region = models.IntegerField()

    class Meta:
        """
        Metadata about the model
        """
        db_table = 'image_region'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['region'], name='image_region_region'),
        ]
        unique_together = ('image', 'region')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RegionImage view for this RegionImage record
        :return: A URL that corresponds to the views for this RegionImage record
        """
        return reverse('region_image_resource', kwargs={'image_id': self.image.pk})
