# stdlib
from collections import deque
from typing import Deque, List
# libs
from cloudcix_rest.models import BaseModel
from django.core.cache import cache
from django.db import models
from django.urls import reverse
# local
from iaas import state, resource_type
from iaas.utils import get_region_cache_key
from .asn import ASN
from .billable_model import BillableModelMixin


__all__ = [
    'Project',
]


class Project(BaseModel):
    """
    A Project is a collection of infrastructure built in the Cloud belonging to a Customer.
    """
    address_id = models.IntegerField()
    archived = models.DateTimeField(null=True)
    closed = models.BooleanField(default=False)
    grace_period = models.IntegerField(default=168, null=True)
    manager_id = models.IntegerField()  # id of the Project's Manager - Send emails to this user
    name = models.CharField(max_length=100)
    note = models.TextField(null=True)
    region_id = models.IntegerField()
    run_icarus = models.BooleanField(default=False)
    run_robot = models.BooleanField(default=False)
    reseller_id = models.IntegerField(null=True)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'project'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='project_id'),
            models.Index(fields=['address_id'], name='project_address_id'),
            models.Index(fields=['archived'], name='project_archived'),
            models.Index(fields=['closed'], name='project_closed'),
            models.Index(fields=['grace_period'], name='project_grace_period'),
            models.Index(fields=['deleted'], name='project_deleted'),
            models.Index(fields=['manager_id'], name='project_manager_id'),
            models.Index(fields=['name'], name='project_name'),
            models.Index(fields=['region_id'], name='project_region_id'),
            models.Index(fields=['run_icarus'], name='project_run_icarus'),
            models.Index(fields=['run_robot'], name='project_run_robot'),
            models.Index(fields=['reseller_id'], name='project_reseller_id'),
        ]
        ordering = ['name']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the ProjectResource view for this Project record
        :return: A URL that corresponds to the views for this Project record
        """
        return reverse('project_resource', kwargs={'pk': self.pk})

    def get_cloud_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the CloudResource view for this Project record
        :return: A URL that corresponds to the Cloud view for this Project record
        """
        return reverse('cloud_resource', kwargs={'pk': self.pk})

    def _check_infrastructure_states(self, states: List[int]) -> bool:
        """
        Checks that every piece of infrastructure in a Project are in the given list of states
        """
        # Integrity
        if self.virtual_router is None:  # pragma: no cover
            status = False
        else:
            status = self.virtual_router.state in states and all([vm.state in states for vm in self.vms.all()])
        return status

    def _check_infrastructure_stable(self) -> bool:
        """
        Check that the project infrastructure is stable
        """
        if self.virtual_router is None:  # pragma: no cover
            status = False
        else:
            status = self.virtual_router.stable and all([vm.stable for vm in self.vms.all()])
        return status

    @property
    def shut_down(self) -> bool:
        """
        Determine if the Project instance is shut down.

        The Project is shut down if all pieces of infrastructure are in deletion states;
            - SCRUB
            - SCRUB_PREP
            - SCRUB_QUEUE
            - SCRUBBING
            - CLOSED
        """
        return self._check_infrastructure_states([
            state.SCRUB,
            state.SCRUB_PREP,
            state.SCRUB_QUEUE,
            state.SCRUBBING,
            state.CLOSED,
        ])

    @property
    def asn(self) -> int:
        """
        Generate the ASN number for this project.
        """
        return ASN.pseudo_asn_offset + self.pk

    @property
    def min_state(self) -> int:
        """
        Calculate the minimum state of an item of infrastructure in the Project
        """
        states: List[int] = [self.virtual_router.state]
        if self.vms.exists():
            states.append(self.vms.aggregate(min_state=models.Min('state'))['min_state'])
        return min(states)

    @property
    def stable(self) -> bool:
        """
        Determine if the Project instance is stable.

        The Project is stable if all pieces of infrastructure are in stable states;
            - RUNNING
            - QUIESCED
            - SCRUB_QUEUE
            - CLOSED
        """
        return self._check_infrastructure_stable()

    def set_deleted(self):
        """
        Delete the Project, and the corresponding ASN
        """
        asn = ASN.objects.get(number=self.pk + ASN.pseudo_asn_offset)
        asn.cascade_delete()

    def set_run_robot_flags(self):
        """
        Set flags that indicates there is changes to infrastructure in the project and region
        """
        self.run_robot = True
        self.run_icarus = True
        self.save()
        cache_key = get_region_cache_key(self.region_id)
        cache.set(cache_key, True)

    def get_billable_models(self) -> Deque[BillableModelMixin]:
        """
        Return a list like object of all the Billable Models associated with this Project
        """
        items: Deque[BillableModelMixin] = deque()

        # Get VMs
        items.extend(self.vms.all())

        # Get VPNs
        items.extend(self.virtual_router.vpn_tunnels.all())

        # Get Resources
        # TODO: Don't return VMs or VPNs here until they are migrated to the Resource model
        items.extend(self.resources.filter(
            resource_type__in=(resource_type.CEPH,)),
        )

        # Return the deque
        return items
