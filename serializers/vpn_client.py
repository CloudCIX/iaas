# libs
import serpy

__all__ = [
    'VPNClientSerializer',
]


class VPNClientSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the VPN Client record was created.
        type: string
    id:
        description: The ID of the VPN Client record
        type: integer
    username:
        description: Name of the client that is allowed through the VPN Tunnel.
        type: string
    password:
        description: Encrypted password of client for VPN.
        type: string
    updated:
        description: Timestamp, in ISO format, of when the Allocation record was last updated.
        type: string
    """

    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    username = serpy.Field()
    password = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
