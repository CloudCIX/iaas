# libs
from cloudcix_rest.controllers import ControllerBase

__all__ = [
    'ServerTypeListController',
]


class ServerTypeListController(ControllerBase):
    """
    Validates User data used to filter a list of Server Types
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'id',
        )

        search_fields = {
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
        }
