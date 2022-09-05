# libs
from cloudcix_rest.controllers import ControllerBase

__all__ = [
    'VPNHistoryListController',
]


class VPNHistoryListController(ControllerBase):
    """
    Validates User data used to filter a list of VPN History
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'created',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'customer_address': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'modified_by': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project_name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'vpn_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
