# stdlib
from typing import Optional
import netaddr
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from .utils import validate_domain_name
from iaas.models import Record

__all__ = [
    'PTRRecordCreateController',
    'PTRRecordUpdateController',
    'PTRRecordListController',
]


class PTRRecordListController(ControllerBase):
    """
    Validates Record data used to filter a list of Record records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'name',
            'content',
            'type',
            'failcontent',
            'time_to_live',
            'ip_address'
            'failover',
            'priority',
            'domain',
            'created',
            'updated',
        )
        search_fields = {
            'content': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'domain': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'failover': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'fail_content': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'ip_address': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'time_to_live': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'type': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class PTRRecordCreateController(ControllerBase):
    """
    Validates Record data used to create a new Record record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Record
        validation_order = (
            'ip_address',
            'content',
            'time_to_live',
        )

    def validate_ip_address(self, ip_address: Optional[str]) -> Optional[str]:
        """
        description: |
            The IP Address that the PTR DNS Record will be set up for.
            The created Record will map the specified IP Address to the specified content value.
            Must be a string containing a valid public IP address.
        type: string
        """
        if ip_address is None:
            return 'iaas_ptr_record_create_101'
        try:
            ip = netaddr.IPAddress(ip_address)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_ptr_record_create_102'
        if ip.is_private():
            return 'iaas_ptr_record_create_103'
        self.cleaned_data['ip_address'] = str(ip)
        return None

    def validate_content(self, content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content of the Record, which is what the given name will map to in the DNS servers.
            Cannot be longer than 255 characters.
        type: string
        """
        if content is None:
            content = ''
        content = str(content).strip()
        if len(content) == 0:
            return 'iaas_ptr_record_create_104'

        # Remove trailing slashes, if any
        if content.endswith('/'):
            content = content[:-1]

        # Validate lengths
        err = validate_domain_name(content, 'iaas_ptr_record_create_105', 'iaas_ptr_record_create_106')
        if err is not None:
            return err

        self.cleaned_data['content'] = content
        return None

    def validate_time_to_live(self, time_to_live: Optional[int]) -> Optional[str]:
        """
        description: |
            The Time To Live (time_to_live) value for the DNS entry, in seconds.
            time_to_live is used to tell DNS servers how long they should hold on to a record before trying to refresh.
            Use a smaller time_to_live if the record will be changing often.
            Cannot be lower than 180 (3 minutes).

            If not sent, defaults to 3600 (1 hour).
        type: integer
        """
        if time_to_live is None:
            time_to_live = 3600

        try:
            time_to_live = int(time_to_live)
        except (TypeError, ValueError):
            return 'iaas_ptr_record_create_107'
        if time_to_live < 180:
            return 'iaas_ptr_record_create_108'

        self.cleaned_data['time_to_live'] = time_to_live
        return None


class PTRRecordUpdateController(ControllerBase):
    """
    Validates Record data used to update an Record record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Record
        validation_order = (
            'content',
            'time_to_live',
        )

    def validate_content(self, content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content of the Record, which is what the given name will map to in the DNS servers.
            Cannot be longer than 255 characters.
        type: string
        """
        if content is None:
            content = ''
        content = str(content).strip()
        if len(content) == 0:
            return 'iaas_ptr_record_update_101'

        # Remove trailing slashes, if any
        if content.endswith('/'):
            content = content[:-1]

        # Validate lengths
        err = validate_domain_name(content, 'iaas_ptr_record_update_102', 'iaas_ptr_record_update_103')
        if err is not None:
            return err

        self.cleaned_data['content'] = content
        return None

    def validate_time_to_live(self, time_to_live: Optional[int]) -> Optional[str]:
        """
        description: |
            The Time To Live (time_to_live) value for the DNS entry, in seconds.
            time_to_live is used to tell DNS servers how long they should hold on to a record before trying to refresh.
            Use a smaller time_to_live if the record will be changing often.
            Cannot be lower than 180 (3 minutes).

            If not sent, defaults to 3600 (1 hour).
        type: integer
        """
        if time_to_live is None:
            time_to_live = 3600

        try:
            time_to_live = int(time_to_live)
        except (TypeError, ValueError):
            return 'iaas_ptr_record_update_104'
        if time_to_live < 180:
            return 'iaas_ptr_record_update_105'

        self.cleaned_data['time_to_live'] = time_to_live
        return None
