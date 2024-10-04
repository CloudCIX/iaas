# stdlib
# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
# local


__all__ = [
    'IPAddressGroup',
]


class IPAddressGroup(BaseModel):
    """
    An IPAddressGroup object represents a IP address group table.
    """
    cidrs = JSONField(default=list)
    member_id = models.IntegerField()
    name = models.CharField(max_length=50)
    version = models.IntegerField(default=4)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'ip_address_group'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='ip_addr_group_id'),
            models.Index(fields=['deleted'], name='ip_addr_group_deleted'),
            models.Index(fields=['member_id'], name='ip_addr_group_member_id'),
            models.Index(fields=['name'], name='ip_addr_group_name'),
            models.Index(fields=['version'], name='ip_addr_group_version'),
        ]
        ordering = ['name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the IPAddressGroupResource view for this IPAddressGroup record
        :return: A URL that corresponds to the views for this IPAddressGroup record
        """
        return reverse('ip_address_group_resource', kwargs={'pk': self.pk})
