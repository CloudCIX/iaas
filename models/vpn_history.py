# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .vpn import VPN

__all__ = [
    'VPNHistory',
]


class VPNHistory(BaseModel):
    """
    A VPNHistory object is created any time a VPN is created or deleted, and it contains details about who modified it
    for billing purposes.
+
    It will be used by automated billing algorithms to calculate how much a VPN cost for the month.
    """
    modified_by = models.IntegerField()
    customer_address = models.IntegerField()
    project_id = models.IntegerField()
    project_name = models.CharField(max_length=100)
    vpn = models.ForeignKey(VPN, related_name='vpn_history', on_delete=models.CASCADE)
    vpn_quantity = models.IntegerField(null=True)
    vpn_sku = models.CharField(max_length=250, null=True)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'vpn_history'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='vpn_history_id'),
            models.Index(fields=['customer_address'], name='vpn_history_customer_address'),
            models.Index(fields=['project_name'], name='vpn_history_project_name'),
            models.Index(fields=['modified_by'], name='vpn_history_modified_by'),
            models.Index(fields=['created'], name='vpn_history_created'),
            models.Index(fields=['deleted'], name='vpn_history_deleted'),
            models.Index(fields=['project_id'], name='vpn_history_project_id'),
        ]
        ordering = ['-created']
