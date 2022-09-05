# lib
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'PoolIP',
]


class PoolIP(BaseModel):
    """

    """
    # Fields
    domain = models.CharField(max_length=240)
    modified_by = models.IntegerField(null=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'pool_ip'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='pool_ip_id'),
            models.Index(fields=['created'], name='pool_ip_created'),
            models.Index(fields=['domain'], name='pool_ip_domain'),
            models.Index(fields=['deleted'], name='pool_ip_deleted'),
            models.Index(fields=['ip_address'], name='pool_ip_ip_address'),
            models.Index(fields=['updated'], name='pool_ip_updated'),
        ]
        ordering = ['created']
        unique_together = ('domain', 'deleted')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the PoolIPResource view for this PoolIP record
        :return: A URL that corresponds to the views for this PoolIP record
        """
        return reverse('pool_ip_resource', kwargs={'pk': self.pk})
