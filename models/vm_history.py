# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
# local
from .vm import VM


__all__ = [
    'VMHistory',
]


class VMHistoryManager(BaseManager):
    """
    Manager for VM which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'storage_histories',
        )


class VMHistory(BaseModel):
    """
    A VMHistory object is created any time a VM is updated, and it contains details about what changes occurred in an
    update, when it was updated and who updated it.

    It will be used by automated billing algorithms to calculate how much a VM cost for the month.
    """
    modified_by = models.IntegerField()
    cpu_quantity = models.IntegerField(null=True)
    cpu_sku = models.CharField(max_length=250, null=True)
    customer_address = models.IntegerField()
    image_quantity = models.IntegerField(null=True)
    image_sku = models.CharField(max_length=250, null=True)
    nat_quantity = models.IntegerField(null=True)
    nat_sku = models.CharField(max_length=250, null=True)
    project_id = models.IntegerField()
    project_vm_name = models.CharField(max_length=228)
    ram_quantity = models.IntegerField(null=True)
    ram_sku = models.CharField(max_length=250, null=True)
    state = models.IntegerField(null=True)
    vm = models.ForeignKey(VM, related_name='history', on_delete=models.CASCADE)

    objects = VMHistoryManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'vm_history'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='vm_history_id'),
            models.Index(fields=['modified_by'], name='vm_history_modified_by'),
            models.Index(fields=['cpu_sku'], name='vm_history_cpu_sku'),
            models.Index(fields=['created'], name='vm_history_created'),
            models.Index(fields=['customer_address'], name='vm_history_customer_address'),
            models.Index(fields=['deleted'], name='vm_history_deleted'),
            models.Index(fields=['image_sku'], name='vm_history_image_sku'),
            models.Index(fields=['nat_sku'], name='vm_history_nat_sku'),
            models.Index(fields=['project_id'], name='vm_history_project_id'),
            models.Index(fields=['ram_sku'], name='vm_history_ram_sku'),
            models.Index(fields=['state'], name='vm_history_state'),
        ]
        ordering = ['-created']
