# stdlib
from datetime import datetime
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'ASN',
]


class ASNManager(BaseManager):
    """
    Manager for ASN that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'allocations',
        )


class ASN(BaseModel):
    """
    An Autonomous System Number (ASN) is issued to organisations by Regional Internet Registry (RIR) such as RIPE.
    Only CIX can modify Allocation records, but they can be assigned to other Members who can then read them.
    """
    # Important constants

    # The normal IANA range for ASNs.
    iana_range = range(1, (2 ** 32) - 1)
    # The offset for pseudo ASNs. All pseudo ASNs must be above this value.
    pseudo_asn_offset = 1000000000000

    # Fields
    member_id = models.IntegerField(null=True)
    number = models.BigIntegerField()

    # Use the new Manager
    objects = ASNManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'asn'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='asn_id'),
            models.Index(fields=['created'], name='asn_created'),
            models.Index(fields=['deleted'], name='asn_deleted'),
            models.Index(fields=['member_id'], name='asn_member_id'),
            models.Index(fields=['number'], name='asn_number'),
            models.Index(fields=['updated'], name='asn_updated'),
        ]
        ordering = ['member_id']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the ASNResource view for this ASN record
        :return: A URL that corresponds to the views for this ASN record
        """
        return reverse('asn_resource', kwargs={'pk': self.pk})

    @property
    def is_pseudo(self) -> bool:
        """
        Return a flag stating whether or not this ASN is a pseudo ASN
        """
        return self.number > self.pseudo_asn_offset

    @property
    def allocations_in_use(self) -> int:
        """
        Return the count of all subnet records that are in use in this Allocation
        """
        return self.allocations.count()

    def cascade_delete(self):
        """
        Set the deleted timestamp of this ASN to the current time, and call this method on all of the Allocations
        belonging to this ASN
        """
        self.deleted = datetime.utcnow()
        self.save()
        for allocation in self.allocations.iterator():
            allocation.cascade_delete()
