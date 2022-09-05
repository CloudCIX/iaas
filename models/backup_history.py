# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .backup import Backup

__all__ = [
    'BackupHistory',
]


class BackupHistory(BaseModel):
    """
    A BackupHistory object is created any time a Backup is created, updated or deleted, and it contains details
    about who modified it for billing purposes.

    It will be used by automated billing algorithms to calculate how much a Backup cost for the month.
    """
    customer_address = models.IntegerField()
    modified_by = models.IntegerField()
    project_id = models.IntegerField()
    backup = models.ForeignKey(Backup, related_name='history', on_delete=models.CASCADE)
    state = models.IntegerField(null=True)
    vm_id = models.IntegerField()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'backup_history'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='backup_history_id'),
            models.Index(fields=['created'], name='backup_history_created'),
            models.Index(fields=['customer_address'], name='backup_history_cust_address'),
            models.Index(fields=['modified_by'], name='backup_history_modified_by'),
            models.Index(fields=['project_id'], name='backup_history_project_id'),
            models.Index(fields=['vm_id'], name='backup_history_vm_id'),
        ]
        ordering = ['-created']
