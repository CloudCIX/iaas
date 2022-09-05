# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from iaas.models import CIXBlacklist

__all__ = [
    'CIXBlacklistListController',
    'CIXBlacklistUpdateController',
    'CIXBlacklistCreateController',
]


class CIXBlacklistListController(ControllerBase):
    """
    Validates CIXBlacklist data used to filter a list of CIXBlacklist records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'cidr',
        )
        search_fields = {
            'cidr': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'comment': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class CIXBlacklistCreateController(ControllerBase):
    """
    Validates CIXBlacklist data used to create a CIXBlacklist record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = CIXBlacklist
        validation_order = (
            'cidr',
            'comment',
        )

    def validate_cidr(self, cidr: Optional[str]) -> Optional[str]:
        """
        description: An address range to block, in CIDR notation.
        type: string
        """
        if cidr is None:
            cidr = ''

        try:
            cidr = str(netaddr.IPNetwork(cidr).cidr)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_cix_blacklist_create_101'

        # Check for duplicates
        if CIXBlacklist.objects.filter(cidr=cidr).exists():
            return 'iaas_cix_blacklist_create_102'

        self.cleaned_data['cidr'] = cidr
        return None

    def validate_comment(self, comment: Optional[str]) -> Optional[str]:
        """
        description: A comment about the blocked CIDR. Can be used to add extra information about the block to a CIDR.
        type: string
        """
        if comment is None:
            comment = ''

        self.cleaned_data['comment'] = str(comment)
        return None


class CIXBlacklistUpdateController(ControllerBase):
    """
    Validates CIXBlacklist data used to update a CIXBlacklist record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = CIXBlacklist
        validation_order = (
            'cidr',
            'comment',
        )

    def validate_cidr(self, cidr: Optional[str]) -> Optional[str]:
        """
        description: An address range to block, in CIDR notation.
        type: string
        """
        if cidr is None:
            cidr = ''

        try:
            cidr = str(netaddr.IPNetwork(cidr).cidr)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_cix_blacklist_update_101'

        # Check for duplicates
        if CIXBlacklist.objects.filter(cidr=cidr).exclude(pk=self._instance.pk).exists():
            return 'iaas_cix_blacklist_update_102'

        self.cleaned_data['cidr'] = cidr
        return None

    def validate_comment(self, comment: Optional[str]) -> Optional[str]:
        """
        description: A comment about the blocked CIDR. Can be used to add extra information about the block to a CIDR.
        type: string
        """
        if comment is None:
            comment = ''

        self.cleaned_data['comment'] = str(comment)
        return None
