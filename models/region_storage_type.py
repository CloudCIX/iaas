# libs
from django.db import models
from django.urls import reverse
# local
from .storage_type import StorageType

__all__ = [
    'RegionStorageType',
]


class RegionStorageType(models.Model):
    """
    A table for handling relationships between StorageTypes and Regions.
    """
    storage_type = models.ForeignKey(StorageType, on_delete=models.CASCADE, related_name='regions')
    region = models.IntegerField()

    class Meta:
        """
        Metadata about the model
        """
        db_table = 'storage_type_region'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['region'], name='storage_type_region_region'),
        ]
        unique_together = ('storage_type', 'region')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RegionStorageType view for this RegionStorageType record
        :return: A URL that corresponds to the views for this RegionStorageType record
        """
        return reverse('region_storage_type_resource', kwargs={'storage_type_id': self.storage_type.pk})
