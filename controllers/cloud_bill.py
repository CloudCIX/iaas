# libs
from cloudcix_rest.controllers import ControllerBase
# local

__all__ = [
    'CloudBillListController',
]


class CloudBillListController(ControllerBase):
    """
    Validates CloudBill data used to filter a list of CloudBill records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        allowed_ordering = (
            'name',
        )
        search_fields = {
            'reseller_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
