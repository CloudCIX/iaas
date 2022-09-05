# stdlib
from typing import Optional
# lib
import netaddr
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Allocation, Subnet

__all__ = [
    'SubnetCreateController',
    'SubnetUpdateController',
    'SubnetListController',
    'SubnetSpaceListController',
]

VALID_VLAN_RANGE = range(0, (2 ** 12) - 1)
VALID_VXLAN_RANGE = range(0, 2 ** 24)


class SubnetListController(ControllerBase):
    """
    Validates Subnet data used to filter a list of Subnet records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'address_range',
            'address_id',
            'created',
            'name',
            'updated',
            'vlan',
            'vxlan',
        )
        search_fields = {
            'address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'address_range': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'allocation_id': ('in',),
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'gateway': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'allocation__asn__member_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'parent_id': ('in', 'isnull'),
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'virtual_router_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vlan': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vxlan': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class SubnetCreateController(ControllerBase):
    """
    Validates Subnet data used to create a new Subnet record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Subnet
        validation_order = (
            'address_id',
            'allocation_id',
            'parent_id',
            'address_range',
            'name',
            'vlan',
            'vxlan',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Address that will own the Subnet.
        type: integer
        """
        # Ensure address_id is sent.
        if address_id is None:
            return 'iaas_subnet_create_101'

        # Ensure address_id is a valid integer.
        try:
            address_id = int(address_id)
        except (TypeError, ValueError):
            return 'iaas_subnet_create_102'

        # If the sent Address ID is the User's Address, return now
        if address_id == self.request.user.address['id']:
            self.cleaned_data['address_id'] = self.request.user.address['id']
            return None

        # If not, ensure the User is linked to the Address
        response = Membership.address.read(
            token=self.request.auth,
            pk=address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_subnet_create_103'

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_allocation_id(self, allocation_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Allocation record that this Subnet will belong to.
            Not required if the Subnet being created is intended for the cloud.
            Required if the Subnet being created is not intended for the cloud, and no parent_id was sent.
        type: integer
        """
        if allocation_id is None:
            return None

        # Ensure allocation_id is a valid integer.
        try:
            allocation_id = int(allocation_id)
        except (TypeError, ValueError):
            return 'iaas_subnet_create_104'

        # Limit the ASN search by Member ID if the requesting User isn't from CIX
        kw = {}
        if self.request.user.member['id'] != 1:
            kw['asn__member_id'] = self.request.user.member['id']

        # Ensure that the ID is valid
        try:
            allocation = Allocation.objects.get(pk=allocation_id, **kw)
        except (TypeError, ValueError, Allocation.DoesNotExist):
            return 'iaas_subnet_create_105'
        self.cleaned_data['allocation'] = allocation
        return None

    def validate_parent_id(self, parent_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Subnet record that will act as the parent to the created record.
            Not required if the Subnet being created is intended for the cloud.
            Required if the Subnet being created is not intended for the cloud, and no allocation_id was sent.
        type: integer
        """
        if parent_id is None:
            return None

        # Ensure parent_id is a valid integer.
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return 'iaas_subnet_create_106'

        # Ensure the ID belongs to an actual record.
        try:
            parent = Subnet.objects.get(pk=parent_id)
        except (ValueError, Subnet.DoesNotExist):
            return 'iaas_subnet_create_107'

        # Check that the parent subnet is also in the sent allocation, if any
        if 'allocation' in self.cleaned_data and self.cleaned_data['allocation'].pk != parent.allocation.pk:
            return 'iaas_subnet_create_108'

        # If the parent subnet is owned by the requesting User's Address, we're fine.
        if parent.address_id == self.request.user.address['id']:
            self.cleaned_data['parent'] = parent
            return None

        if 'address_id' not in self.cleaned_data:
            return None

        # If not, make sure the User's Address is linked to the parent's Address.
        if self.request.user.address['id'] != 1 and parent.address_id != self.cleaned_data['address_id']:
            response = Membership.address.read(
                token=self.request.auth,
                pk=parent.address_id,
                span=self.span,
            )
            # Users in address 1 are allowed to bypass this check
            if response.status_code != 200:
                return 'iaas_subnet_create_109'

        self.cleaned_data['parent'] = parent
        return None

    def validate_address_range(self, address_range: Optional[str]) -> Optional[str]:
        """
        description: |
            The address range for the Subnet, in CIDR form.
            There are subtle differences in how this field is validated depending on whether or not the request is for a
            cloud Subnet.
        type: string
        """
        # Ensure a value was sent
        if address_range is None:
            return 'iaas_subnet_create_110'
        # For all variations, we need to first validate the address_range using netaddr
        try:
            network = netaddr.IPNetwork(address_range)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_subnet_create_111'
        # Remember the new string value of the network
        address_range = str(network)

        # For this version of the method, we need at exactly one of allocation or parent to be present.
        # I think it only takes exactly one of the two, because in the python 2 code I see no handling for if both sent
        allocation = self.cleaned_data.get('allocation', None)
        parent = self.cleaned_data.get('parent', None)
        if allocation is None and parent is None:
            return 'iaas_subnet_create_112'

        # If the allocation was sent - Ensure that the new subnet is the same version as the allocation, and the new
        # subnet does not overlap with any subnet already in the allocation
        if allocation is not None:
            allocation_network = netaddr.IPNetwork(allocation.address_range)
            # First, ensure that the network versions are the same
            if network.version != allocation_network.version:
                return 'iaas_subnet_create_113'
            # Now ensure that the new network is inside the allocation_network
            if network not in allocation_network:
                return 'iaas_subnet_create_114'
            # Also check to make sure the chosen address range doesn't already exist in the Allocation
            if allocation.subnets.filter(address_range=address_range).exists():
                return 'iaas_subnet_create_115'
            # Lastly, check for overlapping subnets
            siblings = netaddr.IPSet(allocation.subnets.values_list('address_range', flat=True))
            for subnet in siblings.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_subnet_create_116'
        # Otherwise, do the same checks but for the parent instead
        if parent is not None:
            parent_network = netaddr.IPNetwork(parent.address_range)
            # First, ensure that the network versions are the same
            if network.version != parent_network.version:
                return 'iaas_subnet_create_117'
            # Check that the address_range is not the same as the parent's
            if address_range == parent.address_range:
                return 'iaas_subnet_create_118'
            # Now ensure that the new network is inside the parent_network
            if network not in parent_network:
                return 'iaas_subnet_create_119'
            # Also check to make sure the chosen address range doesn't already exist in the parent Subnet
            if parent.children.filter(address_range=address_range).exists():
                return 'iaas_subnet_create_120'
            # Lastly, check for overlapping subnets
            siblings = netaddr.IPSet(parent.children.values_list('address_range', flat=True))
            for subnet in siblings.iter_cidrs():
                if network in subnet or subnet in network:
                    return 'iaas_subnet_create_121'
            # Set the allocation of this subnet to be the allocation of the parent Subnet
            self.cleaned_data['allocation'] = parent.allocation
        # At this point, we can also safely save the address_range
        self.cleaned_data['address_range'] = address_range
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            A verbose name for the Subnet record.
            Optional.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        # Ensure the sent name fits in the field.
        if len(name) > self.get_field('name').max_length:
            return 'iaas_subnet_create_122'

        self.cleaned_data['name'] = name
        return None

    def validate_vlan(self, vlan: Optional[int]) -> Optional[str]:
        """
        description: |
            The vlan value in use for the Subnet.
            Must be greater than or equal to 0, and less than 4095.

            If not sent, defaults to 0.
        type: integer
        """
        if vlan is None:
            vlan = 0

        # Ensure it's a valid integer
        try:
            vlan = int(vlan)
        except (TypeError, ValueError):
            return 'iaas_subnet_create_123'

        # Ensure it's within the allowed range.
        if vlan not in VALID_VLAN_RANGE:
            return 'iaas_subnet_create_124'

        self.cleaned_data['vlan'] = vlan
        return None

    def validate_vxlan(self, vxlan: Optional[int]) -> Optional[str]:
        """
        description: |
            The vxlan value in use for the Subnet.
            Must be greater than or equal to 0, and less than 2^24.

            If not sent, defaults to 0.
        type: integer
        """
        if vxlan is None:
            vxlan = 0

        # Ensure it's a valid integer
        try:
            vxlan = int(vxlan)
        except (TypeError, ValueError):
            return 'iaas_subnet_create_125'

        # Ensure it's within the allowed range.
        if vxlan not in VALID_VXLAN_RANGE:
            return 'iaas_subnet_create_126'

        self.cleaned_data['vxlan'] = vxlan
        return None


class SubnetUpdateController(ControllerBase):
    """
    Validates Subnet data used to update a new Subnet record
    """
    _instance: Subnet

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Subnet
        validation_order = (
            'address_id',
            'parent_id',
            'address_range',
            'name',
            'vlan',
            'vxlan',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Address that will own the Subnet.
        type: integer
        """
        # Ensure address_id is sent.
        if address_id is None:
            return 'iaas_subnet_update_101'

        # Ensure address_id is a valid integer.
        try:
            address_id = int(address_id)
        except (TypeError, ValueError):
            return 'iaas_subnet_update_102'

        if address_id == self._instance.address_id:
            self.cleaned_data['address_id'] = address_id
            return None

        if self._instance.cloud:  # pragma: no cover
            return 'iaas_subnet_update_103'

        # If the sent Address ID is the User's Address, return now
        if address_id == self.request.user.address['id']:  # pragma: no cover
            self.cleaned_data['address_id'] = self.request.user.address['id']
            return None

        # If not, ensure the User is linked to the Address
        response = Membership.address.read(
            token=self.request.auth,
            pk=address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_subnet_update_104'

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_parent_id(self, parent_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the Subnet record that will act as the parent to the created record.
        type: integer
        """
        if parent_id is None:
            return None

        if self._instance.cloud:  # pragma: no cover
            return 'iaas_subnet_update_105'

        # Ensure parent_id is a valid integer.
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return 'iaas_subnet_update_106'

        # Ensure the ID belongs to an actual record.
        try:
            parent = Subnet.objects.get(pk=parent_id)
        except (ValueError, Subnet.DoesNotExist):
            return 'iaas_subnet_update_107'

        # Ensure that the parent subnet is in the same allocation as this one because we don't change allocations.
        if self._instance.allocation.pk != parent.allocation.pk:
            return 'iaas_subnet_update_108'

        # If the parent subnet is owned by the requesting User's Address, we're fine.
        if parent.address_id == self.request.user.address['id']:
            self.cleaned_data['parent'] = parent
            return None

        if 'address_id' not in self.cleaned_data:
            return None

        # If not, make sure the User's Address is linked to the parent's Address.
        if self.request.user.address['id'] != 1 and parent.address_id != self.cleaned_data['address_id']:
            response = Membership.address.read(
                token=self.request.auth,
                pk=parent.address_id,
                span=self.span,
            )
            # Users in address 1 are allowed to bypass this check
            if response.status_code != 200:
                return 'iaas_subnet_update_109'

        self.cleaned_data['parent'] = parent  # pragma: no cover
        return None  # pragma: no cover

    def validate_address_range(self, address_range: Optional[str]) -> Optional[str]:
        """
        description: |
            Ensures subnet is a valid subnet. Additionally ensures that subnet
            range does not collide with existing subnets in the allocation.
        type: string
        """
        # Ensure a value was sent
        if address_range is None:
            return 'iaas_subnet_update_110'
        # For all variations, we need to first validate the address_range using netaddr
        try:
            network = netaddr.IPNetwork(address_range)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_subnet_update_111'
        # Remember the new string value of the network
        address_range = str(network)

        # If the address_range hasn't changed, return here
        if address_range == self._instance.address_range:
            return None

        # Ensure that this change to the address range will not orphan any children
        gen = (
            netaddr.IPNetwork(child_subnet.address_range) not in network
            for child_subnet in self._instance.children.all()
        )
        if any(gen):
            return 'iaas_subnet_update_112'

        # Validate the address range against the allocation and / or parent
        allocation = self._instance.allocation
        parent = self.cleaned_data.get('parent', self._instance.parent)

        # Ensure that the new address range is the same version as the allocation, and does not overlap with any subnet
        # already in the allocation
        allocation_network = netaddr.IPNetwork(allocation.address_range)
        # First, ensure that the network versions are the same
        if network.version != allocation_network.version:
            return 'iaas_subnet_update_113'
        # Now ensure that the new network is inside the allocation_network
        if network not in allocation_network:
            return 'iaas_subnet_update_114'
        # Also check to make sure the chosen address range doesn't already exist in the Allocation
        allocation_subnets = allocation.subnets.exclude(pk=self._instance.pk)
        if allocation_subnets.filter(address_range=address_range).exists():
            return 'iaas_subnet_update_115'
        # Lastly, check for overlapping subnets
        siblings = netaddr.IPSet(allocation_subnets.values_list('address_range', flat=True))
        for subnet in siblings.iter_cidrs():
            if network in subnet or subnet in network:
                return 'iaas_subnet_update_116'

        # Also run the same checks for the parent subnet, if any
        if parent is not None:
            parent_network = netaddr.IPNetwork(parent.address_range)
            # First, ensure that the network versions are the same
            if network.version != parent_network.version:
                return 'iaas_subnet_update_117'
            # Now ensure that the new network is inside the parent_network
            if network not in parent_network:
                return 'iaas_subnet_update_118'

        # At this point, we can also safely save the address_range
        self.cleaned_data['address_range'] = address_range  # pragma: no cover
        return None  # pragma: no cover

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            A verbose name for the Subnet record.
            Optional.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        # Ensure the sent name fits in the field.
        if len(name) > self.get_field('name').max_length:
            return 'iaas_subnet_update_119'

        self.cleaned_data['name'] = name
        return None

    def validate_vlan(self, vlan: Optional[int]) -> Optional[str]:
        """
        description: |
            The vlan value in use for the Subnet.
            Must be greater than or equal to 0, and less than 4095.

            If not sent, defaults to 0.
        type: integer
        """
        if vlan is None:
            vlan = 0

        # Ensure it's a valid integer
        try:
            vlan = int(vlan)
        except (TypeError, ValueError):
            return 'iaas_subnet_update_120'

        if vlan == self._instance.vlan:  # pragma: no cover
            return None

        if self._instance.cloud:  # pragma: no cover
            return 'iaas_subnet_update_121'

        # Ensure it's within the allowed range.
        if vlan not in VALID_VLAN_RANGE:
            return 'iaas_subnet_update_122'

        self.cleaned_data['vlan'] = vlan
        return None

    def validate_vxlan(self, vxlan: Optional[int]) -> Optional[str]:
        """
        description: |
            The vxlan value in use for the Subnet.
            Must be greater than or equal to 0, and less than 2^24.

            If not sent, defaults to 0.
        type: integer
        """
        if vxlan is None:
            vxlan = 0

        # Ensure it's a valid integer
        try:
            vxlan = int(vxlan)
        except (TypeError, ValueError):
            return 'iaas_subnet_update_123'

        if vxlan == self._instance.vxlan:
            return None

        if self._instance.cloud:  # pragma: no cover
            return 'iaas_subnet_update_124'

        # Ensure it's within the allowed range.
        if vxlan not in VALID_VXLAN_RANGE:
            return 'iaas_subnet_update_125'

        self.cleaned_data['vxlan'] = vxlan
        return None


class SubnetSpaceListController(ControllerBase):
    """
    Validates Subnet data used to filter a list of Subnet records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'address_range',
        )
        search_fields = {
            'space_type': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
        }
