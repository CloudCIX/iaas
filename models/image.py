# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .server_type import ServerType

__all__ = [
    'Image',
]


class ImageManager(BaseManager):
    """
    Manager for Image which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'regions',
        )


class Image(BaseModel):
    """
    An Image object represents an Operating System image that is supported in the Cloud.
    The support is broken down by region, i.e. some regions may only support some Images.
    """
    answer_file_name = models.CharField(max_length=50, null=True)
    cloud_init = models.BooleanField(default=False)
    display_name = models.CharField(max_length=50)
    filename = models.CharField(max_length=100)
    multiple_ips = models.BooleanField(default=False)
    os_variant = models.CharField(max_length=25, default='rhel6')
    public = models.BooleanField(default=True)
    server_type = models.ForeignKey(ServerType, related_name='images', on_delete=models.PROTECT)

    objects = ImageManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'image'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='image_id'),
            models.Index(fields=['deleted'], name='image_deleted'),
            models.Index(fields=['display_name'], name='image_display_name'),
        ]
        ordering = ['display_name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the ImageResource view for this Image record
        :return: A URL that corresponds to the views for this Image record
        """
        return reverse('image_resource', kwargs={'pk': self.pk})

    def get_regions(self):
        """
        Returns a list of all the regions that this Image is in use
        """
        return list(self.regions.values_list('region', flat=True).iterator())
