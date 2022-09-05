# python
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
import netaddr
# local
from iaas.models import (
    IPMI,
    IPAddress,
)

__all__ = [
    'IPMICreateController',
    'IPMIListController',
]


class IPMIListController(ControllerBase):
    """
    Validates IPMI data used to lists a IMPI
    """
    class Meta(ControllerBase.Meta):
        allowed_ordering = (
            'created',
            'updated',
            'pk',
            'client_ip',
            'customer_ip_id',
            'modified_by',
            'removed',
        )

        search_fields = {
            'client_ip': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'customer_ip_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'modified_by': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'pool_ip__domain': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'removed': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class IPMICreateController(ControllerBase):
    """
    Validates IPMI data used to create a IMPI
    """
    class Meta(ControllerBase.Meta):
        model = IPMI
        validation_order = (
            'client_ip',
            'customer_ip_id',
        )

    def validate_client_ip(self, client_ip: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP address that the customer will be connecting from.
            This is required to ensure that the IPMI rules will be set up just for the IP address.
        type: string
        """
        try:
            netaddr.IPAddress(client_ip)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_ipmi_create_101'
        self.cleaned_data['client_ip'] = client_ip
        return None

    def validate_customer_ip_id(self, customer_ip_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the OOB IPAddress in CloudCIX that the customer wishes to connect to.
        type: integer
        """
        # Ensure that the sent id is a valid integer and corresponds to a valid IPAddress record.
        if customer_ip_id is None:
            return 'iaas_ipmi_create_102'

        try:
            customer_ip = IPAddress.objects.get(pk=int(customer_ip_id))
        except (TypeError, ValueError):
            return 'iaas_ipmi_create_103'
        except IPAddress.DoesNotExist:
            return 'iaas_ipmi_create_104'

        # Ensure that the IPAddress record is in the OOB network
        if customer_ip.subnet.allocation_id != 1:
            return 'iaas_ipmi_create_105'

        self.cleaned_data['customer_ip'] = customer_ip
        return None
