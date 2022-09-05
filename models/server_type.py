# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'ServerType',
]


class ServerType(BaseModel):
    """
    A ServerType object represents a type of Servers we use in the Cloud.
    Some examples are;
        - 1: HyperV Host
        - 2: KVM Host
        - 3: Phantom Host
    """
    name = models.CharField(max_length=50)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'server_type'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='server_type_id'),
            models.Index(fields=['deleted'], name='server_type_deleted'),
            models.Index(fields=['name'], name='server_type_name'),
        ]

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the ServerTypeResource view for this ServerType record
        :return: A URL that corresponds to the views for this ServerType record
        """
        return reverse('server_type_resource', kwargs={'pk': self.pk})
