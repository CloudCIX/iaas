"""
Views for vpn status information from Virtual Routers
"""

# stdlib
import logging
import re
from typing import Any, Dict
# libs
from cloudcix_rest.exceptions import Http404, Http503
from cloudcix_rest.views import APIView
from django.conf import settings
from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import VPN, Router
from iaas.permissions.vpn_status import Permissions

__all__ = [
    'VPNStatusResource',
]


class VPNStatusResource(APIView):
    """
    Gets the vpn status for given vpn id.
    """

    @staticmethod
    def _parse_output(response: tuple, cmd: str) -> str:
        """
        Given a response from the Router, parse it into a proper string
        """
        # remove unwanted character ' \x08' and last two chars '% '
        output = re.sub(' \x08', '', response[1][:-2])
        return output.split(f'{cmd}\r\r\n')[1]

    @staticmethod
    def _parse_ipsec_1(ipsec1: str) -> bool:
        """
        Given a ipsec cmd 1 output info, parse it to find IPsec active or not
        """
        return False if 'Total active tunnels: 0' in ipsec1 else True

    @staticmethod
    def _parse_ipsec_2(ipsec2: str) -> str:
        """
        Given a ipsec cmd 2 output info, parse it to find IPsec status info
        """
        return f'ID: {ipsec2.split("ID: ")[1]}'

    @staticmethod
    def _parse_ike(ike: str) -> bool:
        """
        Given a ike cmd output, parse it to find IKE status
        """
        return 'State: UP' in ike

    @staticmethod
    def _parse_ike_info(ike_raw: str, peer: str, identifier: str) -> str:
        """
        Given a ike raw info, parse it to find requesting VPNs IKE info
        """
        ike_info = ''
        # there can be many vpn tunnels with same remote ip, of all find requesting vpn ike info.
        peer_line = f'IKE peer {peer}'
        for ike in ike_raw.split(peer_line):
            if identifier in ike:
                # found required, add removed peer_line
                ike_info = f'{peer_line}{ike}'
                break
        return ike_info

    def _vpn_status(self, dev: Device, vpn: VPN) -> Dict[str, Any]:  # pragma: no cover
        """
        Sends shell cmds of vpn tunnel ike and ipsec, gathers ike and ipsec states and detailed info
        :param dev: Device instance of SRX router for sending shell cmds
        :param vpn:
        :return: vpn_status dict object
        """
        # definition of vpn status dictionary
        vpn_status: Dict[str, Any] = {
            'ike': False,  # Its True if IKE is 'UP' else False if 'DOWN'
            'ike_info': '',  # Detailed info of IKE phase
            'ipsec': False,  # Its True if IPSec is 'Active' else False if 'Inactive'
            'ipsec_info': '',  # Detailed info of IPSec phase
        }
        project_id = vpn.virtual_router.project.id

        with StartShell(dev) as shell:
            # First get IPsec output as IKE output may be null sometimes.
            # Most of the info can be gathered with IPsec output.

            # IPsec first cmd to get check if ipsec phase is active or not.
            ipsec_cmd_1 = f'cli -c "show security ipsec security-associations vpn-name vrf-' \
                          f'{project_id}-{vpn.stif_number}-ipsec-vpn"'
            ipsec_response_1 = self._parse_output(shell.run(ipsec_cmd_1), ipsec_cmd_1)
            vpn_status['ipsec'] = self._parse_ipsec_1(ipsec_response_1)

            # IPsec second cmd to get vpn IPsec phase information in detail
            ipsec_cmd_2 = f'cli -c "show security ipsec security-associations vpn-name vrf-' \
                          f'{project_id}-{vpn.stif_number}-ipsec-vpn detail | no-more"'
            ipsec_response_2 = self._parse_output(shell.run(ipsec_cmd_2), ipsec_cmd_2)
            vpn_status['ipsec_info'] = self._parse_ipsec_2(ipsec_response_2)

            # IKE cmd to check ike phase is UP or DOWN and its info
            ike_cmd = f'cli -c "show security ike security-associations {vpn.ike_public_ip} ' \
                      f'detail | no-more"'
            # ike cmd may output null even though its UP or DOWN, so try for 5 times else set it to IPSec.
            for _ in range(4):
                ike_info_raw = self._parse_output(shell.run(ike_cmd), ike_cmd)
                if ike_info_raw != '':
                    identifier = f'vrf-{project_id}-{vpn.stif_number}-gateway'
                    vpn_status['ike_info'] = self._parse_ike_info(ike_info_raw, self.vpn.ike_public_ip, identifier)
                    vpn_status['ike'] = self._parse_ike(vpn_status['ike_info'])
                    break
                else:
                    vpn_status['ike'] = vpn_status['ipsec']

        return vpn_status

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Get the VPN status information for the VirtualRouter for a given VPN tunnel.

        description: |
            Connect to a physical Router to pull the VPN status information for the Virtual Router for the chosen
            VPN tunnel.

            The VPN status information is produced from running commands on SRX, one for IKE status and two for IPSEC
            status.

            Each command output processed further to sort the required information and collected into dictionary object.

            Often command output can be null, so command is sent again and again until output is not null.

        path_params:
            pk:
                description: The ID of the VPN to fetch IKE and IPSEC status for
                type: integer

        responses:
            200:
                description: dictionary object with ike and ipsec status info from the Router for the chosen Project.
            403: {}
            404: {}
            503:
                description: An error occurred when connecting to the Router to retrieve vpn status
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER
        logger = logging.getLogger('iaas.views.vpn_status.read')

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                vpn = VPN.objects.get(pk=pk)
            except VPN.DoesNotExist:
                return Http404(error_code='iaas_vpn_status_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, vpn)
            if err is not None:
                return err

        with tracer.start_span('get_router', child_of=request.span):
            router = Router.objects.get(pk=vpn.virtual_router.router.id)
            if router.username is None or router.credentials is None:
                return Http404(error_code='iaas_vpn_status_read_002')

        with tracer.start_span('get_router_mgmt_ip', child_of=request.span):
            management_ip = router.management_ip
            if management_ip == '':
                return Http404(error_code='iaas_vpn_status_read_003')

        if settings.TESTING:
            return Response({'content': []})

        with tracer.start_span('fetching_vpn_status', child_of=request.span):  # pragma: no cover
            try:
                with Device(
                    host=management_ip,
                    user=router.username,
                    password=router.credentials,
                    port=22,
                ) as dev:
                    dev.timeout = 300
                    vpn_status = self._vpn_status(dev=dev, vpn=vpn)
            except Exception:  # pragma: no cover
                logger.error(
                    f'Error occurred when retrieving IKE and IPSEC status for VPN #{pk} '
                    f'from Router @ {management_ip}',
                    exc_info=True,
                )
                return Http503(error_code='iaas_vpn_status_read_004')

        return Response({'content': vpn_status})  # pragma: no cover
