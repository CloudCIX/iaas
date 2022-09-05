# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .vm_history import VMHistory


__all__ = [
    'StorageHistory',
]


class StorageHistory(BaseModel):
    """
    A StorageHistory object is created any time a Storage is created updated or deleted, and it contains details
    about who modified it and what for billing purposes.
+
    It will be used by automated billing algorithms to calculate how much a Storage cost for the month.
    """
    gb_quantity = models.IntegerField(null=True)
    gb_sku = models.CharField(max_length=250, null=True)
    storage_name = models.CharField(max_length=50)
    storage_id = models.IntegerField()
    vm_history = models.ForeignKey(VMHistory, related_name='storage_histories', on_delete=models.CASCADE)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'storage_history'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='storage_history_id'),
            models.Index(fields=['gb_sku'], name='storage_history_gb_sku'),
            models.Index(fields=['storage_id'], name='storage_history_storage_id'),
        ]
        ordering = ['-created']
