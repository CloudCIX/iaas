# lib
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'CIXBlacklist',
]


class CIXBlacklist(BaseModel):
    """

    """
    # Fields
    cidr = models.CharField(max_length=49)
    comment = models.TextField()
    modified_by = models.IntegerField()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'cix_blacklist'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='cix_blacklist_id'),
            models.Index(fields=['cidr'], name='cix_blacklist_cidr'),
            models.Index(fields=['comment'], name='cix_blacklist_comment'),
            models.Index(fields=['created'], name='cix_blacklist_created'),
            models.Index(fields=['deleted'], name='cix_blacklist_deleted'),
            models.Index(fields=['updated'], name='cix_blacklist_updated'),
        ]
        ordering = ['cidr']
        unique_together = ('cidr', 'deleted')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the CIXBlacklistResource view for this CIXBlacklist record
        :return: A URL that corresponds to the views for this CIXBlacklist record
        """
        return reverse('cix_blacklist_resource', kwargs={'cidr': self.cidr})
