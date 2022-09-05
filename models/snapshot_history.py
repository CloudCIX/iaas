# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .snapshot import Snapshot

__all__ = [
    'SnapshotHistory',
]


class SnapshotHistory(BaseModel):
    """
    A SnapshotHistory object is created any time a Snapshot is created, updated or deleted, and it contains details
    about who modified it for billing purposes.

    It will be used by automated billing algorithms to calculate how much a Snapshot cost for the month.
    """
    customer_address = models.IntegerField()
    modified_by = models.IntegerField()
    project_id = models.IntegerField()
    snapshot = models.ForeignKey(Snapshot, related_name='history', on_delete=models.CASCADE)
    state = models.IntegerField(null=True)
    vm_id = models.IntegerField()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'snapshot_history'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='snapshot_history_id'),
            models.Index(fields=['created'], name='snapshot_history_created'),
            models.Index(fields=['customer_address'], name='snapshot_history_cust_address'),
            models.Index(fields=['deleted'], name='snapshot_history_deleted'),
            models.Index(fields=['modified_by'], name='snapshot_history_modified_by'),
            models.Index(fields=['project_id'], name='snapshot_history_project_id'),
            models.Index(fields=['vm_id'], name='snapshot_history_vm_id'),
        ]
        ordering = ['-created']
