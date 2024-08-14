# lib
from cloudcix_rest.models import BaseModel
from django.db import models

__all__ = [
    'DeviceType',
]


class DeviceType(BaseModel):
    """
    A Device Type specifies a family of Devices that CloudCIX supports.
    """
    description = models.TextField()
    sku = models.CharField(max_length=250)

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'device_type'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='device_type_id'),
        ]
        ordering = ['id']
