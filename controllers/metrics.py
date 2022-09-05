# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local

__all__ = [
    'MetricsController',
]


class MetricsController(ControllerBase):
    """
    Using the controller to validate if the user sends a force parameter
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        validation_order = (
            'force',
        )

    def validate_force(self, force: Optional[str]) -> Optional[str]:
        """
        description: A flag stating if the api should ignore the run_icarus flag
        type: boolean
        default: false
        """
        if force is None:
            force = 'false'

        force = str(force).lower()

        if force not in {'true', 'false'}:
            return 'iaas_metrics_read_101'

        self.cleaned_data['force'] = force == 'true'
        return None
