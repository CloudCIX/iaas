# python
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from .utils import validate_domain_name
from iaas.models import PoolIP, IPAddress

__all__ = [
    'PoolIPListController',
    'PoolIPCreateController',
    'PoolIPUpdateController',
]


class PoolIPListController(ControllerBase):
    """
    Validates PoolIP data used to filter a tuple of PoolIP records
    """

    class Meta(ControllerBase.Meta):
        allowed_ordering = (
            'created',
            'updated',
            'ip_address',
            'domain',
        )

        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'domain': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'ip_address': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class PoolIPCreateController(ControllerBase):
    """
    Validates PoolIP data used to create a PoolIP record
    """

    class Meta(ControllerBase.Meta):
        model = PoolIP
        validation_order = (
            'ip_address',
            'domain',
        )

    def validate_ip_address(self, ip_address: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP address to be used for this PoolIP record.
            Must be a string containing a valid IP address.
            Must not be an IP address that is already in the CloudCIX system.
            Must not already be associated with another PoolIP record.
        type: string
        """
        if ip_address is None:
            return 'iaas_pool_ip_create_101'

        # Ensure it's the correct format
        try:
            ip_address = str(netaddr.IPAddress(ip_address))
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_pool_ip_create_101'

        # Ensure there is not other PoolIP records with the same address
        if PoolIP.objects.filter(ip_address=ip_address).exists():
            return 'iaas_pool_ip_create_102'

        # Ensure there are no IPAddress records with the same address
        if IPAddress.objects.filter(address=ip_address).exists():
            return 'iaas_pool_ip_create_103'

        self.cleaned_data['ip_address'] = ip_address
        return None

    def validate_domain(self, domain: Optional[str]) -> Optional[str]:
        """
        description: |
            The domain name to be used for the PoolIP.
            This is the domain name that will be used by Users to connect to the IPMI instance.
            As such, this should be a valid domain name, and a DNS record pointing it to the router should already be
            set up.
            Must be a `.cloudcix.com` domain.
            Must not already be associated with another PoolIP record.
            Must also be a valid domain name (less than 240 characters, each segment <= 63).
        type: string
        """
        if domain is None:
            domain = ''
        domain = str(domain).strip()
        if len(domain) == 0:
            return 'iaas_pool_ip_create_104'

        # Remove trailing slash, if any
        if domain.endswith('/'):
            domain = domain[:-1]

        err = validate_domain_name(domain, 'iaas_pool_ip_create_105', 'iaas_pool_ip_create_106')
        if err is not None:
            return err

        # Ensure that the domain is a cloudcix.com domain
        if not domain.endswith('.cloudcix.com'):
            return 'iaas_pool_ip_create_107'

        # Ensure that there is no other PoolIP record using this domain
        if PoolIP.objects.filter(domain=domain).exists():
            return 'iaas_pool_ip_create_108'

        self.cleaned_data['domain'] = domain
        return None


class PoolIPUpdateController(ControllerBase):
    """
    Validates PoolIP data used to update a PoolIP record
    """
    _instance: PoolIP

    class Meta(ControllerBase.Meta):
        model = PoolIP
        validation_order = (
            'ip_address',
            'domain',
        )

    def validate_ip_address(self, ip_address: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP address to be used for this PoolIP record.
            Must be a string containing a valid IP address.
            Must not be an IP address that is already in the CloudCIX system.
            Must not already be associated with another PoolIP record.
        type: string
        """
        if ip_address is None:
            return 'iaas_pool_ip_update_101'

        # Ensure it's the correct format
        try:
            ip_address = str(netaddr.IPAddress(ip_address))
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_pool_ip_update_101'

        # Ensure there is not other PoolIP records with the same address
        if PoolIP.objects.filter(ip_address=ip_address).exclude(pk=self._instance.pk).exists():
            return 'iaas_pool_ip_update_102'

        # Ensure there are no IPAddress records with the same address
        if IPAddress.objects.filter(address=ip_address).exists():
            return 'iaas_pool_ip_update_103'

        self.cleaned_data['ip_address'] = ip_address
        return None

    def validate_domain(self, domain: Optional[str]) -> Optional[str]:
        """
        description: |
            The domain name to be used for the PoolIP.
            This is the domain name that will be used by Users to connect to the IPMI instance.
            As such, this should be a valid domain name, and a DNS record pointing it to the router should already be
            set up.
            Must be a `.cloudcix.com` domain.
            Must not already be associated with another PoolIP record.
            Must also be a valid domain name (less than 240 characters, each segment <= 63).
        type: string
        """
        if domain is None:
            domain = ''
        domain = str(domain).strip()
        if len(domain) == 0:
            return 'iaas_pool_ip_update_104'

        # Remove trailing slash, if any
        if domain.endswith('/'):
            domain = domain[:-1]

        err = validate_domain_name(domain, 'iaas_pool_ip_update_105', 'iaas_pool_ip_update_106')
        if err is not None:
            return err

        # Ensure that the domain is a cloudcix.com domain
        if not domain.endswith('.cloudcix.com'):
            return 'iaas_pool_ip_update_107'

        # Ensure that there is no other PoolIP record using this domain
        if PoolIP.objects.filter(domain=domain).exists():
            return 'iaas_pool_ip_update_108'

        self.cleaned_data['domain'] = domain
        return None
