# libs
import serpy
# local
from .project import ProjectSerializer
from .virtual_router import VirtualRouterSerializer
from .vm import VMSerializer
from .vpn import VPNSerializer

__all__ = [
    'CloudSerializer',
]


class CloudSerializer(serpy.Serializer):
    """
    project:
        $ref: '#/components/schemas/Project'
    virtual_router:
        $ref: '#/components/schemas/VirtualRouter'
    vms:
        description: An array of VM objects that are in the Project
        type: array
        items:
            $ref: '#/components/schemas/VM'
    vpns:
        description: An array of VPN objects that are in the Virtual Router for the Project
        type: array
        items:
            $ref: '#/components/schemas/VPN'
    """
    project = ProjectSerializer()
    virtual_router = VirtualRouterSerializer()
    vms = VMSerializer(many=True)
    vpns = VPNSerializer(many=True)
