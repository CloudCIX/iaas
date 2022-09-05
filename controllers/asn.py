# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from cloudcix.api.membership import Membership
# local
from iaas.models import ASN

__all__ = [
    'ASNCreateController',
    'ASNUpdateController',
    'ASNListController',
]


class ASNListController(ControllerBase):
    """
    Validates ASN data used to filter a list of ASN records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        max_list_limit = 100
        allowed_ordering = (
            'member_id',
            'number',
            'created',
            'updated',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'member_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class ASNCreateController(ControllerBase):
    """
    Validates ASN data used to create a new ASN record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = ASN
        validation_order = (
            'member_id',
            'number',
        )

    def validate_member_id(self, member_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Member that will own the ASN. Defaults to the Member ID of the requesting User.
        type: integer
        """
        if member_id is None:
            member_id = self.request.user.member['id']

        # If the requested member id is the same as the User's then it's immediately fine
        if member_id == self.request.user.member['id']:
            self.cleaned_data['member_id'] = member_id
            return None

        # If not, attempt to read the Member in question to ensure that the User has permission to make an ASN for them.
        response = Membership.member.read(
            token=self.request.auth,
            pk=member_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_asn_create_101'

        self.cleaned_data['member_id'] = member_id
        return None

    def validate_number(self, number: Optional[int]) -> Optional[str]:
        """
        description: |
            The number value of the ASN.
            The service currently does not accept "asdot" notation, opting instead to only support basic numeric values.
            If "asdot" notation is required, please send an email to `developers (at) cloudcix (dot) com`.
        type: integer
        """
        if number is None:
            return 'iaas_asn_create_102'

        try:
            number = int(number)
        except (TypeError, ValueError):
            return 'iaas_asn_create_102'

        # Check that the number value is within the bounds for an ASN number.
        # ASNs are 32 bit integers, but we also support numbers above one trillion for our Cloud's pseudo-ASNs.
        if number not in ASN.iana_range:
            # If not in this range, check that the value is at least one trillion
            if number <= ASN.pseudo_asn_offset:
                return 'iaas_asn_create_103'

        # Ensure that the number is unique in the DB
        if ASN.objects.filter(number=number).exists():
            return 'iaas_asn_create_104'

        self.cleaned_data['number'] = number

        return None


class ASNUpdateController(ControllerBase):
    """
    Validates ASN data used to update an ASN record
    """
    _instance: ASN

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = ASN
        validation_order = (
            'member_id',
            'number',
        )

    def validate_member_id(self, member_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Member that will own the ASN. Defaults to the Member ID of the requesting User.
        type: integer
        """
        if member_id is None:
            member_id = self.request.user.member['id']

        # If the requested member id is the same as the User's then it's immediately fine
        if member_id == self.request.user.member['id']:
            self.cleaned_data['member_id'] = member_id
            return None

        # If not, attempt to read the Member in question to ensure that the User has permission to make an ASN for them.
        response = Membership.member.read(
            token=self.request.auth,
            pk=member_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'iaas_asn_update_101'

        self.cleaned_data['member_id'] = member_id
        return None

    def validate_number(self, number: Optional[int]) -> Optional[str]:
        """
        description: |
            The number value of the ASN.
            The service currently does not accept "asdot" notation, opting instead to only support basic numeric values.
            If "asdot" notation is required, please send an email to `developers (at) cloudcix (dot) com`.
        type: integer
        """
        if number is None:
            return 'iaas_asn_update_102'
        try:
            number = int(number)
        except (TypeError, ValueError):
            return 'iaas_asn_update_102'

        # Check that the number value is within the bounds for an ASN number.
        # ASNs are 32 bit integers, but we also support numbers above one trillion for our Cloud's pseudo-ASNs.
        if number not in ASN.iana_range:
            # Cannot update an ASN to become a pseudo ASN
            return 'iaas_asn_update_103'

        # Ensure that the number is unique in the DB
        if ASN.objects.filter(number=number).exclude(pk=self._instance.pk).exists():
            return 'iaas_asn_update_104'

        self.cleaned_data['number'] = number
        return None
