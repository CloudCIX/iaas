# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'StorageType',
]


class StorageTypeManager(BaseManager):
    """
    Manager for StorageType which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'regions',
        )


class StorageType(BaseModel):
    """
    A StorageType object represents a type of Storage that is supported in the Cloud.
    The support is broken down by region, i.e. some regions may only support some Storage Types.
    """
    name = models.CharField(max_length=50)

    objects = StorageTypeManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'storage_type'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='storage_type_id'),
            models.Index(fields=['deleted'], name='storage_type_deleted'),
            models.Index(fields=['name'], name='storage_type_name'),
        ]
        ordering = ['name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the StorageTypeResource view for this StorageType record
        :return: A URL that corresponds to the views for this StorageType record
        """
        return reverse('storage_type_resource', kwargs={'pk': self.pk})

    def get_regions(self):
        """
        Returns a list of all the regions that this Storage Type is in use
        """
        return list(self.regions.values_list('region', flat=True).iterator())
