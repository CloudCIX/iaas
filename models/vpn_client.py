# stdlib
# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .vpn import VPN

__all__ = [
    'VPNClient',
]


class VPNClient(BaseModel):
    """
    A VPN client object represents a user data who has access to Dynamic VPN Tunnel.
    """
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=64)
    vpn = models.ForeignKey(VPN, related_name='vpn_clients', on_delete=models.CASCADE)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'vpn_client'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='vpn_client_id'),
        ]
        ordering = ['username']
