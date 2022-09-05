# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Record, Domain

__all__ = [
    'RecordCreateController',
    'RecordUpdateController',
    'RecordListController',
]

VALID_TYPES = {choice[0] for choice in Record.TYPE_CHOICES}
VALID_GEOREGIONS = {choice[0] for choice in Record.GEOREGION_CHOICES}


class RecordListController(ControllerBase):
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
            'failover_content',
            'time_to_live',
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
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'time_to_live': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'type': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class RecordCreateController(ControllerBase):
    """
    Validates Record data used to create a new Record record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Record
        validation_order = (
            'domain_id',
            'type',
            'name',
            'content',
            'time_to_live',
            'priority',
            'georegion',
            'failover',
            'failover_content',
        )

    def validate_domain_id(self, domain_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the CloudCIX domain record that this Record will be linked to.
            Must relate to a valid Domain record in the system.
        type: integer
        """
        if domain_id is None:
            return 'iaas_record_create_101'
        try:
            domain = Domain.objects.get(pk=int(domain_id))
        except (TypeError, ValueError):
            return 'iaas_record_create_102'
        except Domain.DoesNotExist:
            return 'iaas_record_create_103'

        if domain.member_id != self.request.user.member['id']:
            return 'iaas_record_create_104'

        self.cleaned_data['domain'] = domain
        return None

    def validate_type(self, type: Optional[str]) -> Optional[str]:
        """
        description: |
            The type of DNS record to create.
            Below is a list of the types supported by this endpoint.
            For PTR records, there is a separate service under /ptr_record/.

            Allowed types and their ids:
                - NS
                - A
                - AAAA
                - CNAME
                - MX
                - TXT
                - SRV
                - SPF
                - SSHFP
                - LOC
                - NAPTR
        type: string
        """
        if type is None:
            type = ''
        type = str(type).strip()
        if len(type) == 0:
            return 'iaas_record_create_105'

        # Check that the type is one of the allowed types for this view
        if type not in VALID_TYPES:
            return 'iaas_record_create_106'

        if type == Record.PTR:
            return 'iaas_record_create_107'

        self.cleaned_data['type'] = type
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            The name of the Record, used to create the DNS entry.
            Cannot be longer than 80 characters.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_record_create_108'
        if len(name) > self.get_field('name').max_length:
            return 'iaas_record_create_109'

        self.cleaned_data['name'] = name
        return None

    def validate_content(self, content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content of the DNS Record.
            Cannot be longer than 255 characters.
        type: string
        """
        if content is None:
            content = ''
        content = str(content).strip()
        if len(content) == 0:
            return 'iaas_record_create_110'

        # Validate lengths
        if len(content) > self.get_field('content').max_length:
            return 'iaas_record_create_111'

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
            return 'iaas_record_create_112'
        if time_to_live < 180:
            return 'iaas_record_create_113'

        self.cleaned_data['time_to_live'] = time_to_live
        return None

    def validate_priority(self, priority: Optional[int]) -> Optional[str]:
        """
        description: |
            The priority for the DNS record.
            This value is typically used for MX type records, and used to indicate which order to try the records in.
            Cannot be a negative number.

            If not sent, defaults to 1.
        type: integer
        """
        if priority is None:
            priority = 1

        try:
            priority = int(priority)
        except (TypeError, ValueError):
            return 'iaas_record_create_114'
        if priority not in range(1, 65536):
            return 'iaas_record_create_115'

        self.cleaned_data['priority'] = priority
        return None

    def validate_georegion(self, georegion: Optional[int]) -> Optional[str]:
        """
        description: |
            Set the georegion for the DNS record using Rage4.
            Currently, CloudCIX only supports setting records to be available globally.
            At a later stage we hope to add more of the region settings from Rage4.
        type: integer
        """
        self.cleaned_data['georegion'] = Record.GLOBAL
        return None

    def validate_failover(self, failover: Optional[bool]) -> Optional[str]:
        """
        description: |
            Tell Rage4 whether or not to use DNS failover for this Record.
            The Rage4 failover system requires webhooks to work however, as well as requiring a 30 second time_to_live.
            As of yet, the failover system isn't fully supported in CloudCIX, but we have underlying structures in place
            to add support at some point in the future.

            If not sent, defaults to False
        type: boolean
        """
        if failover is None:
            failover = False
        if failover not in {True, False}:
            return 'iaas_record_create_116'
        self.cleaned_data['failover'] = failover
        return None

    def validate_failover_content(self, failover_content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content to be used for failover scenarios.
            When failover occurs, the DNS records will be switched to this content instead.

            Once again, the failover part of Rage4 isn't currently implemented in CloudCIX, but we hope to implement it
            soon.
            This field is optional.
        type: string
        """
        if failover_content is None:
            failover_content = ''
        failover_content = str(failover_content).strip()

        if len(failover_content) > self.get_field('failover_content').max_length:
            return 'iaas_record_create_117'

        self.cleaned_data['failover_content'] = failover_content
        return None


class RecordUpdateController(ControllerBase):
    """
    Validates Record data used to update an Record record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Record
        validation_order = (
            'domain_id',
            'name',
            'content',
            'time_to_live',
            'priority',
            'georegion',
            'failover',
            'failover_content',
        )

    def validate_domain_id(self, domain_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the CloudCIX domain record that this Record will be linked to.
            Must relate to a valid Domain record in the system.
        type: integer
        """
        if domain_id is None:
            return 'iaas_record_update_101'
        try:
            domain = Domain.objects.get(pk=int(domain_id))
        except (TypeError, ValueError):
            return 'iaas_record_update_102'
        except Domain.DoesNotExist:
            return 'iaas_record_update_103'

        if domain.member_id != self.request.user.member['id']:
            return 'iaas_record_update_104'

        self.cleaned_data['domain'] = domain
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            The name of the Record, used to update the DNS entry.
            Cannot be longer than 80 characters.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_record_update_105'
        if len(name) > self.get_field('name').max_length:
            return 'iaas_record_update_106'

        self.cleaned_data['name'] = name
        return None

    def validate_content(self, content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content of the DNS Record.
            Cannot be longer than 255 characters.
        type: string
        """
        if content is None:
            content = ''
        content = str(content).strip()
        if len(content) == 0:
            return 'iaas_record_update_107'

        # Validate lengths
        if len(content) > self.get_field('content').max_length:
            return 'iaas_record_update_108'

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
            return 'iaas_record_update_109'
        if time_to_live < 180:
            return 'iaas_record_update_110'

        self.cleaned_data['time_to_live'] = time_to_live
        return None

    def validate_priority(self, priority: Optional[int]) -> Optional[str]:
        """
        description: |
            The priority for the DNS record.
            This value is typically used for MX type records, and used to indicate which order to try the records in.
            Cannot be a negative number.

            If not sent, defaults to 0.
        type: integer
        """
        if priority is None:
            priority = 1

        try:
            priority = int(priority)
        except (TypeError, ValueError):
            return 'iaas_record_update_111'
        if priority not in range(1, 65536):
            return 'iaas_record_update_112'

        self.cleaned_data['priority'] = priority
        return None

    def validate_georegion(self, georegion: Optional[int]) -> Optional[str]:
        """
        description: |
            Set the georegion for the DNS record using Rage4.
            Currently, CloudCIX only supports setting records to be available globally.
            At a later stage we hope to add more of the region settings from Rage4.
        type: integer
        """
        self.cleaned_data['georegion'] = Record.GLOBAL
        return None

    def validate_failover(self, failover: Optional[bool]) -> Optional[str]:
        """
        description: |
            Tell Rage4 whether or not to use DNS failover for this Record.
            The Rage4 failover system requires webhooks to work however, as well as requiring a 30 second time_to_live.
            As of yet, the failover system isn't fully supported in CloudCIX, but we have underlying structures in place
            to add support at some point in the future.

            If not sent, defaults to False
        type: boolean
        """
        if failover is None:
            failover = False
        if failover not in {True, False}:
            return 'iaas_record_update_113'
        self.cleaned_data['failover'] = failover
        return None

    def validate_failover_content(self, failover_content: Optional[str]) -> Optional[str]:
        """
        description: |
            The content to be used for failover scenarios.
            When failover occurs, the DNS records will be switched to this content instead.

            Once again, the failover part of Rage4 isn't currently implemented in CloudCIX, but we hope to implement it
            soon.
            This field is optional.
        type: string
        """
        if failover_content is None:
            failover_content = ''
        failover_content = str(failover_content).strip()

        # Validate lengths
        if len(failover_content) > self.get_field('failover_content').max_length:
            return 'iaas_record_update_114'

        self.cleaned_data['failover_content'] = failover_content
        return None
