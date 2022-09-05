# stdlib
from typing import List, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from iaas.models import Project

__all__ = [
    'RunRobotTurnOffController',
]


class RunRobotTurnOffController(ControllerBase):
    """
    Validates ASN data used to create a new ASN record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the Controller.Meta fields
        """
        validation_order = (
            'project_ids',
        )

    def validate_project_ids(self, project_ids: Optional[List[int]]) -> Optional[str]:
        """
        description: |
            An array of IDs of projects in the requesting users region
        type: array
        items:
            type: integer
        """

        # Ensure the value sent is a list.
        project_ids = project_ids or []
        if not isinstance(project_ids, list):
            return 'iaas_run_robot_turn_off_101'

        if len(project_ids) == 0:
            return 'iaas_run_robot_turn_off_102'

        # Check if all sent values are integers.
        try:
            project_id_set = {int(project) for project in project_ids}
        except (TypeError, ValueError):
            return 'iaas_run_robot_turn_off_103'

        # Verify the ids are all projects
        proj_ids = list(project_id_set)
        if Project.objects.filter(id__in=proj_ids, region_id=self.request.user.address['id']).count() != len(proj_ids):
            return 'iaas_run_robot_turn_off_104'

        self.project_ids = proj_ids
        return None
