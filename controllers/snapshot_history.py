# libs
from cloudcix_rest.controllers import ControllerBase

__all__ = [
    'SnapshotHistoryListController',
]


class SnapshotHistoryListController(ControllerBase):
    """
    Validates User data used to filter a list of snapshot History
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
            'snapshot_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
