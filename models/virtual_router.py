# stdlib
from datetime import datetime, timedelta
from typing import List
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from iaas import state as states
from .ip_address import IPAddress
from .project import Project
from .router import Router
from .subnet import Subnet

__all__ = [
    'VirtualRouter',
]


class VirtualRouterManager(BaseManager):
    """
    Manager for VirtualRouter which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'ip_address',
            'project',
            'router',
        ).prefetch_related(
            'firewall_rules',
            'vpn_tunnels',
        )


class VirtualRouter(BaseModel):
    """
    A VirtualRouter object represents a virtual routing table in a physical Router.
    Each Project has one Virtual Router.
    """
    ip_address = models.ForeignKey(IPAddress, on_delete=models.PROTECT)
    project = models.OneToOneField(Project, related_name='virtual_router', on_delete=models.CASCADE)
    router = models.ForeignKey(Router, related_name='virtual_routers', on_delete=models.PROTECT)
    state = models.IntegerField(default=states.IN_API)  # Start states at -1 instead of 0

    objects = VirtualRouterManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'virtual_router'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='virtual_router_id'),
            models.Index(fields=['deleted'], name='virtual_router_deleted'),
            models.Index(fields=['state'], name='virtual_router_state'),
        ]
        ordering = ['project__name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the VirtualRouterResource view for this VirtualRouter record
        :return: A URL that corresponds to the views for this VirtualRouter record
        """
        return reverse('virtual_router_resource', kwargs={'pk': self.pk})

    def get_subnets(self) -> List[Subnet]:
        """
        Retrieve the Subnet details for this VirtualRouter instance
        """
        subnets = Subnet.objects.filter(virtual_router_id=self.pk).values(
            'address_id',
            'address_range',
            'id',
            'modified_by',
            'name',
            'vlan',
            'vxlan',
        ).iterator()

        return subnets

    def can_update(self) -> bool:
        """
        Can this Virtual Router currently be updated?
        """
        # Use the User state change map to determine if the update from current state to
        # RUNNING_UPDATE or QUIESCED_UPDATE is allowed
        return states.RUNNING_UPDATE in states.USER_STATE_MAP.get(self.state, {}) or \
            states.QUIESCED_UPDATE in states.USER_STATE_MAP.get(self.state, {})

    @property
    def scrub_queue_time_passed(self):
        if self.state == states.SCRUB_QUEUE:
            return self.updated + timedelta(hours=self.project.grace_period) < datetime.now()
        return False

    @property
    def stable(self):
        """
        Determine if the Virtual Router instance is stable.

        The Virtual Router is stable if it is in a stable state:
            - RUNNING
            - QUIESCED
            - SCRUB_QUEUE
            - CLOSED
        """

        return self.state in states.STABLE_STATES

    def set_deleted(self):
        """
        Delete the Virtual Router, it's IP Address Subnets, VPNs and Firewall Rules,
        """
        now = datetime.now()
        self.ip_address.cascade_delete()
        Subnet.objects.filter(virtual_router_id=self.pk).update(deleted=now)
        for vpn in self.vpn_tunnels.all():
            # When brought into products model VPN will be updated to have state = Closed
            vpn.deleted = now
            vpn.save()
        for rule in self.firewall_rules.all():
            # When brought into products model Rule will be updated to have state = Closed
            rule.deleted = now
            rule.save()
        # Close project
        self.project.closed = True
        self.project.save()
        self.project.set_deleted()

    # Override .save() to save the VPN tunnels if the state changes to one of the states to create BOMs for
    def save(self, *args, **kwargs):
        super(VirtualRouter, self).save(*args, **kwargs)
        self.refresh_from_db()

        if self.state in states.BOM_CREATE_STATES:
            # Save all the VPNs associated with this Virtual Router
            for vpn in self.vpn_tunnels.all():
                vpn.save()
