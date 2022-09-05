# libs
from cloudcix_rest.controllers import ControllerBase

__all__ = [
    'VMHistoryListController',
]


class VMHistoryListController(ControllerBase):
    """
    Validates User data used to filter a list of VM History
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'created',
        )
        search_fields = {
            'cpu_sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'customer_address': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'image_sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'modified_by': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'nat_sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'ram_sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'storage_histories__gb_sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'storage_histories__storage_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'vm_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
