# stdlib
from datetime import datetime
from random import randint
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse

__all__ = [
    'Domain',
]


class DomainManager(BaseManager):
    """
    Manager for Domain that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'records',
        )


class Domain(BaseModel):
    """

    """
    # Fields
    # Atypical primary key as it needs to coincide with the rage4 id
    id = models.IntegerField(primary_key=True)
    member_id = models.IntegerField()
    modified_by = models.IntegerField(null=True)
    # For both Domain and Record;
    # - max_length should be 240
    # - ensure that each segment when split on '.' is <= 63 characters long
    name = models.CharField(max_length=240)

    # Use the new Manager
    objects = DomainManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'domain'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='domain_id'),
            models.Index(fields=['created'], name='domain_created'),
            models.Index(fields=['deleted'], name='domain_deleted'),
            models.Index(fields=['member_id'], name='domain_member_id'),
            models.Index(fields=['name'], name='domain_name'),
            models.Index(fields=['updated'], name='domain_updated'),
        ]
        ordering = ['name']
        unique_together = ('name', 'deleted')

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the DomainResource view for this Domain record
        :return: A URL that corresponds to the views for this Domain record
        """
        return reverse('domain_resource', kwargs={'pk': self.pk})

    def cascade_delete(self):
        """
        Delete this object and all of its children
        """
        deltime = datetime.utcnow()
        self.deleted = deltime
        self.save()

        for record in self.records.iterator():
            record.deleted = deltime
            record.save()

    @classmethod
    def get_random_id(cls) -> int:
        """
        Generate a random ID that doesn't overlap with any existing ID, for test purposes
        """
        existing = {pk for pk in cls.objects.values_list('pk', flat=True)}
        pk = randint(1, 2 ** 16)
        while pk in existing:  # pragma: no cover
            pk = randint(1, 2 ** 16)
        return pk
