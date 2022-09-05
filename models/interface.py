# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse
# local
from .server import Server

__all__ = [
    'Interface',
]


class Interface(BaseModel):
    """
    A Interface object represents a physical Interface on a Server.
    Interfaces can have some accompanying data with them, including mac addresses, ip addresses and dns names.
    """
    details = models.CharField(max_length=64, default='')
    enabled = models.BooleanField(default=False)
    hostname = models.CharField(max_length=64, default='')
    ip_address = models.GenericIPAddressField(null=True)
    mac_address = models.CharField(max_length=17)
    server = models.ForeignKey(Server, related_name='interfaces', on_delete=models.CASCADE)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'interface'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='interface_id'),
            models.Index(fields=['deleted'], name='interface_deleted'),
            models.Index(fields=['details'], name='interface_details'),
            models.Index(fields=['enabled'], name='interface_enabled'),
            models.Index(fields=['hostname'], name='interface_hostname'),
            models.Index(fields=['ip_address'], name='interface_ip_address'),
            models.Index(fields=['mac_address'], name='interface_mac_address'),
        ]
        ordering = ['created']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RouterResource view for this Interface record
        :return: A URL that corresponds to the views for this Interface record
        """
        return reverse('interface_resource', kwargs={'pk': self.pk})
