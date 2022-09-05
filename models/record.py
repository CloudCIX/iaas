# stdlib
from random import randint
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .domain import Domain

__all__ = [
    'Record',
]


class RecordManager(BaseManager):
    """
    Manager for Record that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related('domain').exclude(type='PTR')


class PTRRecordManager(BaseManager):
    """
    Manager for Record that fetches only PTR Records
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related('domain').filter(type='PTR')


class Record(BaseModel):
    """

    """
    # Record Type Constants and Choices
    NS = 'NS'
    A = 'A'
    AAAA = 'AAAA'
    CNAME = 'CNAME'
    MX = 'MX'
    TXT = 'TXT'
    SRV = 'SRV'
    PTR = 'PTR'
    SPF = 'SPF'
    SSHFP = 'SSHFP'
    LOC = 'LOC'
    NAPTR = 'NAPTR'

    TYPE_CHOICES = (
        (NS, NS),
        (A, A),
        (AAAA, AAAA),
        (CNAME, CNAME),
        (MX, MX),
        (TXT, TXT),
        (SRV, SRV),
        (PTR, PTR),
        (SPF, SPF),
        (SSHFP, SSHFP),
        (LOC, LOC),
        (NAPTR, NAPTR),
    )

    # Georegion Constants and Choices
    GLOBAL = 0
    GEOREGION_CHOICES = (
        (GLOBAL, 'Global'),
    )

    # Fields
    content = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, related_name='records', on_delete=models.PROTECT, null=True)
    failover = models.BooleanField(default=False)
    failover_content = models.CharField(max_length=255, default='')
    georegion = models.IntegerField(choices=GEOREGION_CHOICES)
    # Atypical primary key as it needs to coincide with the rage4 id
    id = models.IntegerField(primary_key=True)
    member_id = models.IntegerField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    modified_by = models.IntegerField(null=True)
    name = models.CharField(max_length=80)
    priority = models.IntegerField(null=True)
    time_to_live = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # Use the new Managers
    objects = RecordManager()
    ptr_objects = PTRRecordManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'record'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='record_id'),
            models.Index(fields=['created'], name='record_created'),
            models.Index(fields=['content'], name='record_content'),
            models.Index(fields=['deleted'], name='record_deleted'),
            models.Index(fields=['failover'], name='record_failover'),
            models.Index(fields=['failover_content'], name='record_failover_content'),
            models.Index(fields=['ip_address'], name='record_ip_address'),
            models.Index(fields=['name'], name='record_name'),
            models.Index(fields=['time_to_live'], name='record_time_to_live'),
            models.Index(fields=['type'], name='record_type'),
            models.Index(fields=['updated'], name='record_updated'),
        ]
        ordering = ['name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the RecordResource view for this Record record.
        This method checks whether the record is a forward or reverse record by checking if the type is PTR, and returns
        the corresponding URL.
        :return: A URL that corresponds to the views for this Record record
        """
        url_name: str
        if self.type == self.PTR:
            url_name = 'ptr_record_resource'
        else:
            url_name = 'record_resource'
        return reverse(url_name, kwargs={'pk': self.pk})

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
