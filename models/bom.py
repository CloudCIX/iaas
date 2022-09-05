# libs
from django.db import models
# local
from .vm import VM
from .vpn import VPN

__all__ = [
    'BOM',
]


class BOM(models.Model):
    """
    BOM stands for Bill of Materials.
    Entries in this model will be linking SKU quantities (and quantity changes) to the various objects in the system.

    `created` is not automatic, so we can link it to the updated timestamp of the object in question.

    Whenever the object is moved into a state where we don't bill for, we can just set all the SKUs for it to 0
    """
    created = models.DateTimeField()
    quantity = models.IntegerField()
    sku = models.CharField(max_length=250)
    vm = models.ForeignKey(VM, related_name='skus', on_delete=models.CASCADE, null=True)
    vpn = models.ForeignKey(VPN, related_name='skus', on_delete=models.CASCADE, null=True)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'bom'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='bom_id'),
            models.Index(fields=['created'], name='bom_created'),
            models.Index(fields=['quantity'], name='bom_quantity'),
            models.Index(fields=['sku'], name='bom_sku'),
        ]
        ordering = ['created']
