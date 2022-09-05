# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from iaas import state as states
from .vm import VM


__all__ = [
    'Backup',
]


class BackupManager(BaseManager):
    """
    Manager for Backup which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'vm',
        ).prefetch_related(
            'history',
        )


class Backup(BaseModel):
    """
    A backup is full duplication of vm data, stored separate to the original vm's host.
    Backups can be restored in the event of a problem or loss of a vm.
    """
    name = models.CharField(max_length=128, null=True)
    repository = models.IntegerField()
    state = models.IntegerField()
    time_valid = models.DateTimeField(blank=True, null=True)
    vm = models.ForeignKey(VM, models.CASCADE, related_name='backups')

    objects = BackupManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'backup'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='backup_id'),
            models.Index(fields=['name'], name='backup_name'),
            models.Index(fields=['repository'], name='backup_repository'),
            models.Index(fields=['state'], name='backup_state'),
            models.Index(fields=['time_valid'], name='backup_time_valid'),
        ]
        ordering = ['time_valid']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the AllocationResource view for this backup record
        :return: A URL that corresponds to the views for this backup record
        """
        return reverse('backup_resource', kwargs={'pk': self.pk})

    def can_update(self) -> bool:
        """
        Can this Backup currently be updated?
        """
        return not Backup.objects.filter(
            vm_id=self.vm.id,
        ).exclude(
            state__in=states.STABLE_STATES,
        ).exists()
