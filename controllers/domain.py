# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from .utils import validate_domain_name
from iaas.models import Domain

__all__ = [
    'DomainCreateController',
    'DomainListController',
]


class DomainListController(ControllerBase):
    """
    Validates Domain data used to filter a list of Domain records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'name',
            'created',
            'updated',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'member_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class DomainCreateController(ControllerBase):
    """
    Validates Domain data used to create a new Domain record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        model = Domain
        validation_order = (
            'name',
        )

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: The domain name for the record.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()
        if len(name) == 0:
            return 'iaas_domain_create_101'

        # Remove trailing slash, if any
        if name.endswith('/'):
            name = name[:-1]

        # Validate the domain name for length and segment length
        err = validate_domain_name(name, 'iaas_domain_create_102', 'iaas_domain_create_103')
        if err is not None:
            return err

        self.cleaned_data['name'] = name
        return None
