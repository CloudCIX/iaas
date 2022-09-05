# libs
from django.db import models
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
