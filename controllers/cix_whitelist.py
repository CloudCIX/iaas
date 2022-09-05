# python
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from iaas.models import CIXWhitelist

__all__ = [
    'CIXWhitelistListController',
    'CIXWhitelistCreateController',
    'CIXWhitelistUpdateController',
]


class CIXWhitelistListController(ControllerBase):
    """
    Validates CIXWhitelist data used to filter a tuple of CIXWhitelist records
    """

    class Meta(ControllerBase.Meta):
        allowed_ordering = (
            'cidr',
            'created',
            'updated',
        )

        search_fields = {
            'cidr': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'comment': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class CIXWhitelistCreateController(ControllerBase):
    """
    Validates CIXWhitelist data used to create a CIXWhitelist record
    """

    class Meta(ControllerBase.Meta):
        model = CIXWhitelist
        validation_order = (
            'cidr',
            'comment',
        )

    def validate_cidr(self, cidr: Optional[str]) -> Optional[str]:
        """
        description: The address range to be whitelisted, in CIDR notation.
        type: string
        """
        if cidr is None:
            cidr = ''

        try:
            cidr = str(netaddr.IPNetwork(cidr).cidr)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_cix_whitelist_create_101'

        # Check for a potential duplicate (overlap doesn't matter)
        if CIXWhitelist.objects.filter(cidr=cidr).exists():
            return 'iaas_cix_whitelist_create_102'

        self.cleaned_data['cidr'] = cidr
        return None

    def validate_comment(self, comment: str) -> Optional[str]:
        """
        description: |
            A comment about the whitelisted CIDR.
            Can be used to give extra information about why this CIDR is whitelisted.
        type: string
        """
        if comment is None:
            comment = ''

        self.cleaned_data['comment'] = str(comment)
        return None


class CIXWhitelistUpdateController(ControllerBase):

    class Meta(ControllerBase.Meta):
        model = CIXWhitelist
        validation_order = (
            'cidr',
            'comment',
        )

    def validate_cidr(self, cidr: str) -> Optional[str]:
        """
        description: The address range to be whitelisted, in CIDR notation.
        type: string
        """
        if cidr is None:
            cidr = ''

        try:
            cidr = str(netaddr.IPNetwork(cidr).cidr)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_cix_whitelist_update_101'

        # Check for a potential duplicate
        if CIXWhitelist.objects.filter(cidr=cidr).exclude(pk=self._instance.pk).exists():
            return 'iaas_cix_whitelist_update_102'

        self.cleaned_data['cidr'] = cidr
        return None

    def validate_comment(self, comment) -> Optional[str]:
        """
        description: |
            A comment about the whitelisted CIDR.
            Can be used to give extra information about why this CIDR is whitelisted.
        type: string
        """
        if comment is None:
            comment = ''

        self.cleaned_data['comment'] = str(comment)
        return None
