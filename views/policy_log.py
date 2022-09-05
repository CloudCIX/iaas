"""
Views for log messages from Virtual Routers
"""

# stdlib
import logging
import re
from typing import Dict, List, Optional
# libs
from cloudcix_rest.exceptions import Http404, Http503
from cloudcix_rest.views import APIView
from django.conf import settings
from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import Project, Router
from iaas.permissions.policy_log import Permissions

__all__ = [
    'PolicyLogCollection',
]

DENY_PATTERN = re.compile('RT_FLOW_SESSION_DENY')
DATA_PATTERN = re.compile(
    r'\<14\>1\s'
    r'(?P<timestamp>\d{4}-\d{2}-\d+T\d{2}:\d{2}:\d{2}.\d+Z).+'
    r'source-address="(?P<source_address>[\da-fA-F\.:]+)".+'
    r'source-port="(?P<source_port>\d+)".+'
    r'destination-address="(?P<destination_address>[\da-fA-F\.:]+)".+'
    r'destination-port="(?P<destination_port>\d+)".+'
    r'service-name="(?:junos-)?(?P<service_name>[a-z\-]+|None)"',
)


class PolicyLogCollection(APIView):
    """
    List
    """

    @staticmethod
    def _parse_log(log: str) -> Optional[Dict[str, str]]:
        """
        Given a log from the Router, parse it into a dictionary
        """
        access = 'ALLOWED'
        if DENY_PATTERN.search(log) is not None:
            access = 'BLOCKED'

        # Match the Data Pattern and get the groupdict
        match = DATA_PATTERN.match(log)
        if match is None:
            return None
        return dict(access=access, **match.groupdict())

    def get(self, request: Request, project_id: int) -> Response:
        """
        summary: Get the latest log messages for the VirtualRouter for a given Project.

        description: |
            Connect to a physical Router to pull the 15 most recent log messages for the Virtual Router for the chosen
            Project.

            The returned list is in descending order of time, meaning the first item in the returned list is the latest
            message at the time of request.

            If there are any errors when parsing log messages, this service will return less than 15 messages.

        path_params:
            project_id:
                description: The ID of the Project to fetch logs for
                type: integer

        responses:
            200:
                description: 15 Latest log messages from the Router for the chosen Project.
            403: {}
            404: {}
            503:
                description: An error occurred when connecting to the Router to retrieve logs
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER
        logger = logging.getLogger('iaas.views.policy_log.list')

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_policy_log_list_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request, project)
            if err is not None:
                return err

        with tracer.start_span('get_router', child_of=request.span):
            router = Router.objects.get(region_id=project.region_id)
            if router.username is None or router.credentials is None:
                return Http404(error_code='iaas_policy_log_list_002')

        with tracer.start_span('get_router_mgmt_ip', child_of=request.span):
            management_ip = router.management_ip
            if management_ip == '':
                return Http404(error_code='iaas_policy_log_list_003')

        if settings.TESTING:
            return Response({'content': []})

        with tracer.start_span('fetching_logs', child_of=request.span):  # pragma: no cover
            try:
                with Device(
                    host=management_ip,
                    port=22,
                    user=router.username,
                    password=router.credentials,
                ) as dev:
                    with StartShell(dev) as shell:
                        # Cat the whole file, grep and THEN tail for the last 15 lines
                        cmd = f'cat /var/log/policy_session | grep vrf-{project_id} | tail -n 15'
                        response = shell.run(cmd)
            except Exception:  # pragma: no cover
                logger.error(
                    f'Error occurred when retrieving Policy Logs for Project #{project_id} '
                    f'from Router @ {management_ip}',
                    exc_info=True,
                )
                return Http503(error_code='iaas_policy_log_list_004')

        with tracer.start_span('parsing_logs', child_of=request.span):  # pragma: no cover
            # We already know how long the return list will be, 15 items
            logs: List[Dict[str, str]] = [{} for _ in range(15)]

            # Split the response on new lines, and trim excess chars
            raw = [line.strip() for line in response[1]]

            # Iterate in reverse order, skip the first and last item
            log_index = 0
            for raw_index in range(len(raw) - 2, 1, -1):
                parsed = self._parse_log(raw[raw_index])
                if parsed is None:
                    # Don't throw an error, just skip
                    logger.warning(f'Could not parse log line for Project #{project_id}\n{raw[raw_index]}')
                    continue
                logs[log_index] = parsed
                log_index += 1

            # Filter out the empty log lines
            logs = list(filter(None, logs))

        return Response({'content': logs})  # pragma: no cover
