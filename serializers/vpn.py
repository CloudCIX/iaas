# libs
import serpy
# local
from .route import RouteSerializer
from .vpn_client import VPNClientSerializer

__all__ = [
    'BaseVPNSerializer',
    'VPNSerializer',
]


class BaseVPNSerializer(serpy.Serializer):
    """
    created:
        description: The date that the VPN entry was created
        type: string
    description:
        description: A verbose text field used to describe what the vpn is used for.
        type: string
    dns:
        description: The IP Address of the customer preferred dns record that is setup to the VPN Tunnel
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified vpn configuration .
        type: array
        items:
            type: string
    id:
        description: The ID of the VPN record.
        type: integer
    ike_authentication:
        description: |
            A string containing a comma separated array of authentication algorithm names in use for the IKE phase of
            the VPN
        type: string
    ike_dh_groups:
        description: |
            A string containing a comma separated array of diffie-helmen groups in use for the IKE phase of the VPN
        type: string
    ike_gateway_type:
        description: |
            A string defining the type of gateway used in the VPN.
        type: string
    ike_gateway_value:
        description: |
            A string containing the value for the gateway for the VPN.
            Will be appropriate data to match the gateway type.
        type:
            string
    ike_encryption:
        description: |
            A string containing a comma separated array of encryption algorithm names in use for the IKE phase of
            the VPN
        type: string
    ike_lifetime:
        description: The time in seconds that the IKE phase should be kept alive for before re-establishing
        type: integer
    ike_local_identifier:
        description: |
            A string containing the value for the local (Project) IKE identifier for the VPN.
            It's default value is local-<vpn_id>-<region_id>.<organisation_url> .
        type:
            string
    ike_pre_shared_key:
        description: The pre-shared key to be used in setting up the VPN Tunnel
        type: string
    ike_remote_identifier:
        description: |
            A string containing the value for the remote (Non-Project) IKE identifier for the VPN.
            It's default value is remote-<vpn_id>-<region_id>.<organisation_url> .
        type:
            string
    ike_version:
        description: The IKE version in use for the VPN Tunnel;
        type: string
    ipsec_authentication:
        description: |
            A string containing a comma separated array of authentication algorithm names in use for the IPSec phase of
            the VPN
        type: string
    ipsec_encryption:
        description: |
            A string containing a comma separated array of encryption algorithm names in use for the IPSec phase of
            the VPN
        type: string
    ipsec_establish_time:
        description: |
            A string containing the time at which the tunnel should be established (either immediately or once it first
            receives traffic)
        type: string
    ipsec_pfs_groups:
        description: |
            A string containing a comma separated array of Perfect Forward Secrecy group names in use for the IPSec
            phase of the VPN
        type: string
        nullable: yes
    ipsec_lifetime:
        description: The time in seconds that the IPSec phase should be kept alive for before re-establishing
        type: integer
    send_email:
        description: If True, VPN details will be sent by mail by Robot after Robot builds VPN on Router.
        type: boolean
    stif_number:
        description: Represents the st interface number, a logical interface id, to uniquely define VPN on SRX.
        type: Integer
    traffic_selector:
        description: |
            Flag stating if each of the local and remote subnets will be added to the configuration negotiation with
            peer or 0.0.0.0/0 is used.
        type: Boolean
    updated:
        description: The date that the VPN entry was last updated
        type: string
    uri:
        description: The absolute URL of the VirtualRouter that can be used to perform `Read`, `Update` and `Delete`
        type: string
    virtual_router_id:
        description: The ID of the Virtual Router that houses the VPN Tunnel
        type: integer
    vpn_type:
        description: VPN Types supported by CloudCIX, valid options are 'site_to_site' and 'dynamic_secure_connect'
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    description = serpy.Field()
    dns = serpy.Field()
    emails = serpy.Field(required=False)
    id = serpy.Field()
    ike_authentication = serpy.Field()
    ike_dh_groups = serpy.Field()
    ike_gateway_type = serpy.Field()
    ike_gateway_value = serpy.Field()
    ike_encryption = serpy.Field()
    ike_lifetime = serpy.Field()
    ike_local_identifier = serpy.Field()
    ike_pre_shared_key = serpy.Field()
    ike_remote_identifier = serpy.Field()
    ike_version = serpy.Field()
    ipsec_authentication = serpy.Field()
    ipsec_encryption = serpy.Field()
    ipsec_establish_time = serpy.Field()
    ipsec_pfs_groups = serpy.Field()
    ipsec_lifetime = serpy.Field()
    send_email = serpy.Field()
    stif_number = serpy.Field()
    traffic_selector = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    virtual_router_id = serpy.Field()
    vpn_type = serpy.Field()


class VPNSerializer(BaseVPNSerializer):
    """
    created:
        description: The date that the VPN entry was created
        type: string
    description:
        description: A verbose text field used to describe what the vpn is used for.
        type: string
    dns:
        description: The IP Address of the customer preferred dns record that is setup to the VPN Tunnel
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified vpn configuration .
        type: array
        items:
            type: string
    id:
        description: The ID of the VPN record.
        type: integer
    ike_authentication:
        description: |
            A string containing a comma separated array of authentication algorithm names in use for the IKE phase of
            the VPN
        type: string
    ike_dh_groups:
        description: |
            A string containing a comma separated array of diffie-helmen groups in use for the IKE phase of the VPN
        type: string
    ike_gateway_type:
        description: |
            A string defining the type of gateway used in the VPN.
        type: string
    ike_gateway_value:
        description: |
            A string containing the value for the gateway for the VPN.
            Will be appropriate data to match the gateway type.
        type:
            string
    ike_encryption:
        description: |
            A string containing a comma separated array of encryption algorithm names in use for the IKE phase of
            the VPN
        type: string
    ike_lifetime:
        description: The time in seconds that the IKE phase should be kept alive for before re-establishing
        type: integer
    ike_local_identifier:
        description: |
            A string containing the value for the local (Project) IKE identifier for the VPN.
            It's default value is local-<vpn_id>-<region_id>.<organisation_url> .
        type:
            string
    ike_pre_shared_key:
        description: The pre-shared key to be used in setting up the VPN Tunnel
        type: string
    ike_remote_identifier:
        description: |
            A string containing the value for the remote (Non-Project) IKE identifier for the VPN.
            It's default value is remote-<vpn_id>-<region_id>.<organisation_url> .
        type:
            string
    ike_version:
        description: The IKE version in use for the VPN Tunnel;
        type: string
    ipsec_authentication:
        description: |
            A string containing a comma separated array of authentication algorithm names in use for the IPSec phase of
            the VPN
        type: string
    ipsec_encryption:
        description: |
            A string containing a comma separated array of encryption algorithm names in use for the IPSec phase of
            the VPN
        type: string
    ipsec_establish_time:
        description: |
            A string containing the time at which the tunnel should be established (either immediately or once it first
            receives traffic)
        type: string
    ipsec_pfs_groups:
        description: |
            A string containing a comma separated array of Perfect Forward Secrecy group names in use for the IPSec
            phase of the VPN
        type: string
        nullable: yes
    ipsec_lifetime:
        description: The time in seconds that the IPSec phase should be kept alive for before re-establishing
        type: integer
    routes:
        description: An array of user defined Routes in the VPN.
        type: array
        items:
            $ref: '#/components/schemas/Route'
    send_email:
        description: If True, VPN details will be sent by mail by Robot after Robot builds VPN on Router.
        type: boolean
    stif_number:
        description: Represents the st interface number, a logical interface id, to uniquely define VPN on SRX.
        type: Integer
    traffic_selector:
        description: |
            Flag stating if each of the local and remote subnets will be added to the configuration negotiation with
            peer or 0.0.0.0/0 is used.
        type: Boolean
    updated:
        description: The date that the VPN entry was last updated
        type: string
    uri:
        description: The absolute URL of the VirtualRouter that can be used to perform `Read`, `Update` and `Delete`
        type: string
    virtual_router_id:
        description: The ID of the Virtual Router that houses the VPN Tunnel
        type: integer
    vpn_clients:
        description: An array of user defined clients for the VPN.
        type: array
        items:
            $ref: '#/components/schemas/VPNClient'
    vpn_type:
        description: VPN Types supported by CloudCIX, valid options are 'site_to_site' and 'dynamic_secure_connect'
        type: string
    """
    routes = RouteSerializer(attr='routes.iterator', call=True, many=True)
    vpn_clients = VPNClientSerializer(attr='vpn_clients.iterator', call=True, many=True)
