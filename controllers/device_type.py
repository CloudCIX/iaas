# stdlib
# libs
from cloudcix_rest.controllers import ControllerBase
# local


__all__ = [
    'DeviceTypeListController',
]


class DeviceTypeListController(ControllerBase):
    """
    Lists the device types.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of ControllerBase meta to make it more specific to the DeviceTypeList.
        """
        allowed_ordering = (
            'description',
            'id',
            'sku',
        )
        search_fields = {
            'description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'sku': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
        }
