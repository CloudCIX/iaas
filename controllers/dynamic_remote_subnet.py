# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local

__all__ = [
    'DynamicRemoteSubnetController',
]


class DynamicRemoteSubnetController(ControllerBase):
    """
    Using the controller to validate if the user sends a search parameter for remote subnet
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        validation_order = (
            'dynamic_remote_subnet',
        )

    def validate_dynamic_remote_subnet(self, dynamic_remote_subnet: Optional[str]) -> Optional[str]:
        """
        description: A string to search for available dynamic_remote_subnet
        type: str
        default: false
        """
        if dynamic_remote_subnet is None:
            return None

        self.cleaned_data['dynamic_remote_subnet'] = dynamic_remote_subnet
        return None
