# stdlib
import re
from typing import List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from iaas.models import IPAddressGroup


__all__ = [
    'IPAddressGroupListController',
    'IPAddressGroupUpdateController',
    'IPAddressGroupCreateController',
]
# first character is a letter
# aplhanumberic allowed
# underscore allowed
# hyphen allowed
NAME_REGEX = re.compile('^[a-zA-Z][a-zA-Z0-9_-]*$')


class IPAddressGroupListController(ControllerBase):
    """
    Validates IPAddressGroup data used to filter a list of IPAddressGroup records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'name',
            'created',
            'member_id',
            'updated',
            'version',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'member_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'version': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class IPAddressGroupCreateController(ControllerBase):
    """
    Validates IPAddressGroup data used to create a IPAddressGroup record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = IPAddressGroup
        validation_order = (
            'member_id',
            'name',
            'version',
            'cidrs',
        )

    def validate_member_id(self, member_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The member_id owner of the IP Address Group. It defaults to the requesting users member_id.
            Users in Member 1 can create public list available for all members by sending 0 as the value for member_id.
            An example of a public list is for Geo Location groups based on Country.
        type: integer
        required: false
        """
        if member_id is None:
            member_id = self.request.user.member_id

        try:
            member_id = int(member_id)
        except (TypeError, ValueError):
            return 'iaas_ip_address_group_create_101'

        self.cleaned_data['member_id'] = member_id
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name to be given to the new IP Address Group
        type: string
        """
        # name is sent
        if name is None:
            name = ''
        name = str(name).strip()
        if NAME_REGEX.match(name) is None:
            return 'iaas_ip_address_group_create_102'

        if 'member_id' not in self.cleaned_data:
            return None
        member_id = self.cleaned_data['member_id']

        # Check name is unique for IP Address Group in member_id
        if IPAddressGroup.objects.filter(name=name, member_id=member_id).exists():
            return 'iaas_ip_address_group_create_103'

        self.cleaned_data['name'] = name
        return None

    def validate_version(self, version: Optional[int]) -> Optional[str]:
        """
        description: |
            The IP version of the IP Address Group Objects in the IP Address Group. Accepted versions are 4 and 6.
            If not sent, it will default to 4.
        type: integer
        required: false
        """
        if version is None:
            version = 4

        try:
            version = int(version)
        except (TypeError, ValueError):
            return 'iaas_ip_address_group_create_104'

        if version not in (4, 6):
            return 'iaas_ip_address_group_create_105'

        self.cleaned_data['version'] = version
        return None

    def validate_cidrs(self, cidrs: Optional[List[str]]) -> Optional[str]:
        """
        description: A array of CIDR addresses in the IP Address Group.
        type: array
        items:
            type: string
        """
        if not isinstance(cidrs, list):
            return 'iaas_ip_address_group_create_106'

        if len(cidrs) == 0:
            return 'iaas_ip_address_group_create_107'

        if 'version' not in self.cleaned_data:
            return None

        group_version = self.cleaned_data['version']
        results = []
        for cidr in cidrs:
            try:
                network = netaddr.IPNetwork(cidr.strip())
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_ip_address_group_create_108'

            if network.version != group_version:
                return 'iaas_ip_address_group_create_109'

            results.append(str(network.cidr))

        self.cleaned_data['cidrs'] = results
        return None


class IPAddressGroupUpdateController(ControllerBase):
    """
    Validates IPAddressGroup data used to update a IPAddressGroup record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = IPAddressGroup
        validation_order = (
            'name',
            'version',
            'cidrs',
        )

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name to be given to the new IP Address Group
        type: string
        required: false
        """
        # name is sent
        if name is None:
            return None
        name = str(name).strip()
        if NAME_REGEX.match(name) is None:
            return 'iaas_ip_address_group_update_101'

        # Check name is unique for IP Address Group in member_id
        if IPAddressGroup.objects.filter(
            name=name,
            member_id=self._instance.member_id,
        ).exclude(pk=self._instance.pk).exists():
            return 'iaas_ip_address_group_update_102'

        self.cleaned_data['name'] = name
        return None

    def validate_version(self, version: Optional[int]) -> Optional[str]:
        """
        description: |
            The IP version of the IP Address Group Objects in the IP Address Group. Accepted versions are 4 and 6.
        type: integer
        required: false
        """
        if version is None:
            return None

        try:
            version = int(version)
        except (TypeError, ValueError):
            return 'iaas_ip_address_group_update_103'

        if version not in (4, 6):
            return 'iaas_ip_address_group_update_104'

        self.cleaned_data['version'] = version
        return None

    def validate_cidrs(self, cidrs: Optional[List[str]]) -> Optional[str]:
        """
        description: An array of CIDR addresses in the IP Address Group.
        type: array
        items:
            type: string
        """
        if not isinstance(cidrs, list):
            return 'iaas_ip_address_group_update_105'

        if len(cidrs) == 0:
            return 'iaas_ip_address_group_update_106'

        group_version = self.cleaned_data.get('version', self._instance.version)
        results = []
        for cidr in cidrs:
            try:
                network = netaddr.IPNetwork(cidr.strip())
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_ip_address_group_update_107'

            if network.version != group_version:
                return 'iaas_ip_address_group_update_108'
            results.append(str(network.cidr))

        self.cleaned_data['cidrs'] = results
        return None
