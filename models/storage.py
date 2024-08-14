# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse
# local
from .vm import VM
from .storage_history import StorageHistory

__all__ = [
    'Storage',
]


class Storage(BaseModel):
    """
    A Storage object represents a disk attached to a VM
    """
    gb = models.IntegerField()
    name = models.CharField(max_length=50)
    primary = models.BooleanField(default=False)
    vm = models.ForeignKey(VM, related_name='storages', on_delete=models.CASCADE)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'storage'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='storage_id'),
            models.Index(fields=['deleted'], name='storage_deleted'),
            models.Index(fields=['name'], name='storage_name'),
            models.Index(fields=['primary'], name='storage_primary'),
        ]
        ordering = ['-primary', 'name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the StorageResource view for this Storage record
        :return: A URL that corresponds to the views for this Storage record
        """
        return reverse('storage_resource', kwargs={'pk': self.pk, 'vm_id': self.vm.id})

    def get_history(self):
        """
        Retrieve the Storage History details for this Storage instance
        """
        return StorageHistory.objects.filter(
            deleted__isnull=True,
            storage_id=self.pk,
        ).values('gb_quantity', 'gb_sku', 'storage_id', 'storage_name').order_by('-created')
