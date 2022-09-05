# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import Project

__all__ = [
    'Permissions',
]


class Permissions:
    """
    Checks the permissions of the views.Project methods
    """

    @staticmethod
    def list(request: Request, obj: Project) -> Optional[Http403]:
        """
        The request to list PolicyLogs for a Project is valid if;
        - The requesting User owns to chosen Project.
        """
        if request.user.id == 1:  # pragma: no cover
            return None

        if obj.address_id != request.user.address['id']:
            return Http403(error_code='iaas_policy_log_list_201')

        return None
