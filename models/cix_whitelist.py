# lib
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'CIXWhitelist',
]


class CIXWhitelist(BaseModel):
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
        db_table = 'cix_whitelist'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='cix_whitelist_id'),
            models.Index(fields=['cidr'], name='cix_whitelist_cidr'),
            models.Index(fields=['comment'], name='cix_whitelist_comment'),
            models.Index(fields=['created'], name='cix_whitelist_created'),
            models.Index(fields=['deleted'], name='cix_whitelist_deleted'),
            models.Index(fields=['updated'], name='cix_whitelist_updated'),
        ]
        ordering = ['cidr']
        unique_together = ('cidr', 'deleted')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the CIXWhitelistResource view for this CIXWhitelist record
        :return: A URL that corresponds to the views for this CIXWhitelist record
        """
        return reverse('cix_whitelist_resource', kwargs={'cidr': self.cidr})
