# stdlib
from typing import Any, Dict, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
from django.conf import settings
from jaeger_client import Span
from rest_framework.request import QueryDict, Request
# local
from iaas.models import Allocation, Project
from .asn import ASNCreateController
from .virtual_router import VirtualRouterCreateController

__all__ = [
    'ProjectCreateController',
    'ProjectListController',
    'ProjectUpdateController',
]

ALLOWED_UPDATE_STATES = {4, 8}


class ProjectListController(ControllerBase):
    """
    Validates User data used to filter a list of Projects
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'name',
            'region_id',
            'address_id',
            'created',
            'manager_id',
        )
        search_fields = {
            'address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'archived': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'closed': (),
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'manager_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'note': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'reseller_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'run_icarus': (),
            'run_robot': (),
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class ProjectCreateController(ControllerBase):
    """
    Validates User data used to create a Project
    """
    instance: Project

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        model = Project
        validation_order = (
            'region_id',
            'name',
            'note',
        )

    def __init__(self, request: Request, data: QueryDict, span: Optional[Span]) -> None:
        """
        Override the init to allow for adding extra fields from outside into the system.
        :param request: The request sent by the User
        :param data: The data being validated. Either request.GET or request.POST depending on the method
        :param span: A Span instance that is the parent span of the controller. Passing this in will allow us to record
                     time taken to run the validation methods in the controller.
        """
        super(ProjectCreateController, self).__init__(request=request, data=data, span=span)
        self.cleaned_data['address_id'] = request.user.address['id']
        self.cleaned_data['manager_id'] = request.user.id

    def save(self, span: Span) -> Optional[Dict[str, Any]]:
        """
        Save the Project model and create the other necessary models for the Project
        """
        tracer = settings.TRACER

        # Firstly, save the instance
        with tracer.start_span('saving_object', child_of=span):
            self.instance.save()

        # Next, create the Virtual Router
        with tracer.start_span('creating_virtual_router', child_of=span) as child_span:
            virtual_router_controller = VirtualRouterCreateController(
                data={'project_id': self.instance.id},
                request=self.request,
                span=child_span,
            )
            if not virtual_router_controller.is_valid():
                self.instance.delete()
                return {'errors': virtual_router_controller.errors}

        with tracer.start_span('saving_virtual_router', child_of=span):
            virtual_router_controller.cleaned_data.pop('router_ip_addresses')
            virtual_router_controller.instance.save()
            self.instance.refresh_from_db()

        with tracer.start_span('creating_project_asn', child_of=span) as child_span:
            data = {
                'member_id': self.request.user.member['id'],
                'number': self.instance.asn,
            }
            asn_controller = ASNCreateController(
                data=data,
                request=self.request,
                span=child_span,
            )

            if not asn_controller.is_valid():  # pragma: no cover
                virtual_router_controller.instance.delete()
                self.instance.delete()
                return {'errors': asn_controller.errors}

        with tracer.start_span('saving_project_asn', child_of=span) as child_span:
            asn_controller.instance.save()

        with tracer.start_span('creating_pseudo_allocations', child_of=span) as child_span:
            # Create the private allocations for the ASN in question.
            Allocation.create_pseudo(self.request, asn_controller.instance)

        return None

    def validate_region_id(self, region_id: Optional[int]) -> Optional[str]:
        """
        description: The Address ID of the CloudCIX region that the Project will be deployed in.
        type: integer
        """
        if region_id is None:
            return 'iaas_project_create_101'

        try:
            region_id = int(region_id)
        except (ValueError, TypeError):
            return 'iaas_project_create_102'

        # TODO: Need to know the API call to membership first to get this information before implementing
        # When seller address is added as a validation field to project, verify requesting address for project is a
        # cloud_customer and the requesting address has set the seller address as a cloud_seller
        # To verify region, the region's billing address_id must give the seller address the cloud_disti role
        # and the cloud_reseller the region's billing_address_id, the cloud_builder role

        response = Membership.cloud_bill.read(
            token=self.request.auth,
            address_id=region_id,
            target_address_id=self.request.user.address['id'],
            pk=None,
            span=self.span,
        )
        if response.status_code != 200:  # pragma: no cover
            return 'iaas_project_create_103'

        if not response.json()['content']['is_region'] or not response.json()['content']['cloud_customer']:
            return 'iaas_project_create_104'

        self.cleaned_data['region_id'] = region_id
        # TODO: Allow user to select reseller - currently is billing_address for region address or region address
        self.cleaned_data['reseller_id'] = response.json()['content']['reseller_id']
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the Project. Must be unique within an Address' Project collection.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_project_create_105'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_project_create_106'

        if Project.objects.filter(name=name, address_id=self.request.user.address['id']).exclude(closed=True).exists():
            return 'iaas_project_create_107'

        self.cleaned_data['name'] = name
        return None

    def validate_note(self, note: Optional[str]) -> Optional[str]:
        """
        description: A note about the project to store information. No length limit.
        type: string
        required: false
        """
        self.cleaned_data['note'] = str(note).strip() if note else ''
        return None


class ProjectUpdateController(ControllerBase):
    """
    Validates User data used to update a Project
    """
    _instance: Project

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        model = Project
        validation_order = (
            'name',
            'note',
            'state',
        )

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the Project. Must be unique within an Address' Project collection.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_project_update_101'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_project_update_102'

        if Project.objects.filter(
            name=name,
            address_id=self.request.user.address['id'],
        ).exclude(pk=self._instance.pk).exclude(closed=True).exists():
            return 'iaas_project_update_103'

        self.cleaned_data['name'] = name
        return None

    def validate_note(self, note: Optional[str]) -> Optional[str]:
        """
        description: A note about the project to store information. No length limit.
        type: string
        required: false
        """
        self.cleaned_data['note'] = str(note).strip() if note else self._instance.note
        return None

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: |
            The Project's overall state. This is used for quickly choosing to delete or restore a Project without having
            to request the deletion of every VM in the Project separately. Note that this can only be done when the
            Project is in a stable state, meaning that no operations are being carried out or are scheduled for the
            Project. Also, the minimum state of the Project must be RUNNING (4) as well.

            Sending a value of 8 when the Project is running will cause every VM in the Project to be moved into the
            "Requested for Deletion" state.

            Sending a value of 4 when the Project is in the "Requested for Deletion" state will move every VM back into
            the state that it was in before they were moved to the "Requested for Deletion" state (defaults to QUIESCED)
        type: integer
        """
        if state is None:
            return None

        if self._instance.min_state < 4:
            return 'iaas_project_update_104'

        try:
            state = int(state)
        except (ValueError, TypeError):
            return 'iaas_project_update_105'

        if state not in ALLOWED_UPDATE_STATES:
            return 'iaas_project_update_106'

        if not self._instance.stable:
            return 'iaas_project_update_107'

        if state == 8 and self._instance.shut_down:
            return 'iaas_project_update_108'

        if state == 4 and not self._instance.shut_down:
            return 'iaas_project_update_109'

        self.cleaned_data['state'] = state
        return None
