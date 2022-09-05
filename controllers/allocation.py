# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
from cloudcix.api.membership import Membership
# local
from iaas.models import Allocation, ASN

__all__ = [
    'AllocationCreateController',
    'AllocationUpdateController',
    'AllocationListController',
]


class AllocationListController(ControllerBase):
    """
    Validates Allocation data used to filter a list of Allocation records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        max_list_limit = 100
        allowed_ordering = (
            'address_range',
            'asn__number',
            'name',
            'created',
            'updated',
        )
        search_fields = {
            'address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'address_range': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'asn_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'asn__number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class AllocationCreateController(ControllerBase):
    """
    Validates Allocation data used to create a new Allocation record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Allocation
        validation_order = (
            'address_id',
            'asn_id',
            'address_range',
            'name',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Address that the Allocation is being allocated to.
            If not sent, will default to the Address ID of the requesting User.
        type: integer
        """
        if address_id is None:
            address_id = self.request.user.address['id']

        # If the requested address id is the same as the User's then it's immediately fine
        if address_id == self.request.user.address['id']:
            self.cleaned_data['address_id'] = address_id
            return None

        # If not, we need to try and read the chosen Address.
        # If we cannot, then there is an error with this request.
        response = Membership.address.read(
            token=self.request.auth,
            pk=address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_allocation_create_101'

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_asn_id(self, asn_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the ASN object to assign the Allocation to.
            Must be an ASN in the requesting User's Member.
        type: integer
        """
        # First check that it has a value
        if asn_id is None:
            return 'iaas_allocation_create_102'

        # Next, check if we need to add an extra keyword to the fetch.
        kw = {}
        if self.request.user.member['id'] != 1:
            kw['member_id'] = self.request.user.member['id']

        # Try and fetch the ASN object.
        try:
            asn_id = int(asn_id)
            asn = ASN.objects.get(id=asn_id, **kw)
        except (TypeError, ValueError):
            return 'iaas_allocation_create_102'
        except ASN.DoesNotExist:
            return 'iaas_allocation_create_103'

        self.cleaned_data['asn'] = asn
        return None

    def validate_address_range(self, address_range: Optional[str]) -> Optional[str]:
        """
        description: |
            The range of IP addresses within the Allocation in CIDR form.
            The range cannot overlap with any other Allocations in the chosen ASN.
        type: string
        """
        if 'asn' not in self.cleaned_data:
            return None
        asn: ASN = self.cleaned_data['asn']

        if address_range is None:
            return 'iaas_allocation_create_104'

        try:
            network = netaddr.IPNetwork(address_range)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_allocation_create_104'

        # Check for overlap
        existing = netaddr.IPSet(asn.allocations.values_list('address_range', flat=True))
        for existing_network in existing.iter_cidrs():
            if network in existing_network or existing_network in network:
                return 'iaas_allocation_create_105'

        self.cleaned_data['address_range'] = address_range
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name for the Allocation record.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_allocation_create_106'
        if len(name) > self.get_field('name').max_length:
            return 'iaas_allocation_create_107'
        self.cleaned_data['name'] = name
        return None


class AllocationUpdateController(ControllerBase):
    """
    Validates Allocation data used to update an Allocation record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Allocation
        validation_order = (
            'address_id',
            'asn_id',
            'address_range',
            'name',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Address that the Allocation is being allocated to.
            If not sent, will default to the Address ID of the requesting User.
        type: integer
        """
        if address_id is None:
            address_id = self.request.user.address['id']

        # If the requested address id is the same as the User's then it's immediately fine
        if address_id == self.request.user.address['id']:
            self.cleaned_data['address_id'] = address_id
            return None

        # If not, we need to try and read the chosen Address.
        # If we cannot, then there is an error with this request.
        response = Membership.address.read(
            token=self.request.auth,
            pk=address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_allocation_update_101'

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_asn_id(self, asn_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the ASN object to assign the Allocation to.
            Must be an ASN in the requesting User's Member.
        type: integer
        """
        # First check that it has a value
        if asn_id is None:
            return 'iaas_allocation_update_102'

        # Next, check if we need to add an extra keyword to the fetch.
        kw = {}
        if self.request.user.member['id'] != 1:
            kw['member_id'] = self.request.user.member['id']

        # Try and fetch the ASN object.
        try:
            asn_id = int(asn_id)
            asn = ASN.objects.get(id=asn_id, **kw)
        except (TypeError, ValueError):
            return 'iaas_allocation_update_102'
        except ASN.DoesNotExist:
            return 'iaas_allocation_update_103'

        self.cleaned_data['asn'] = asn
        return None

    def validate_address_range(self, address_range: Optional[str]) -> Optional[str]:
        """
        description: |
            The range of IP addresses within the Allocation in CIDR form.
            The range cannot overlap with any other Allocations in the chosen ASN.
        type: string
        """
        asn: ASN = self.cleaned_data.get('asn', self._instance.asn)

        if address_range is None:
            return 'iaas_allocation_update_104'

        try:
            network = netaddr.IPNetwork(address_range)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_allocation_update_104'

        # Check for overlap
        existing = netaddr.IPSet(asn.allocations.exclude(pk=self._instance.pk).values_list('address_range', flat=True))
        for existing_network in existing.iter_cidrs():
            if network in existing_network or existing_network in network:
                return 'iaas_allocation_update_105'

        self.cleaned_data['address_range'] = address_range
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name for the Allocation record.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_allocation_update_106'
        if len(name) > self.get_field('name').max_length:
            return 'iaas_allocation_update_107'
        self.cleaned_data['name'] = name
        return None
