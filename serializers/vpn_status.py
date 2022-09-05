# libs
import serpy

__all__ = [
    'VPNStatusSerializer',
]


class VPNStatusSerializer(serpy.Serializer):
    """
    ike:
        description: IKE is True if it UP or False when DOWN.
        type: bool
    ike_info:
        description: The detailed information about IKE Phase of VPN Tunnel from the Router.
        type: string
    ipsec:
        description: IPSec is True if it active or False when inactive.
        type: bool
    ipsec_info:
        description: The detailed information about IPSec Phase of VPN Tunnel from the Router
        type: string
    """
    ike = serpy.Field()
    ike_info = serpy.Field()
    ipsec = serpy.Field()
    ipsec_info = serpy.Field()
