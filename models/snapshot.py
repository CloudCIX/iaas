# stdlib
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from iaas import state as states
from .vm import VM
from iaas.serializers import SnapshotTreeSerializer

__all__ = [
    'Snapshot',
]


class SnapshotManager(BaseManager):
    """
    Manager for VM which pre-fetches foreign keys
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


class Snapshot(BaseModel):
    """
    A Snapshot record is the state of a system at a particular point in time.
    It can be used to preserve the state of a VM, and revert back to that point in time.
    """

    active = models.BooleanField()
    name = models.CharField(max_length=128)
    parent = models.ForeignKey('self', models.CASCADE, related_name='children', null=True)
    remove_subtree = models.BooleanField(default=False)
    state = models.IntegerField()
    vm = models.ForeignKey(VM, models.CASCADE, related_name='snapshots')

    objects = SnapshotManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'snapshot'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='snapshot_id'),
            models.Index(fields=['active'], name='snapshot_active'),
            models.Index(fields=['name'], name='snapshot_name'),
            models.Index(fields=['remove_subtree'], name='snapshot_remove_subtree'),
            models.Index(fields=['state'], name='snapshot_state'),
        ]

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the AllocationResource view for this snapshot record
        :return: A URL that corresponds to the views for this snapshot record
        """
        return reverse('snapshot_resource', kwargs={'pk': self.pk})

    def get_children(self):
        """
        Retrieve the Children Snapshot details for this VirtualRouter instance
        """
        """ self referral field """
        children = SnapshotTreeSerializer(
            instance=self.children.all(),
            many=True,
        )
        return children.data

    def can_update(self) -> bool:
        """
        Can this Snapshot currently be updated?
        """
        return not Snapshot.objects.filter(
            vm_id=self.vm.id,
        ).exclude(
            state__in=states.STABLE_STATES,
        ).exists()
