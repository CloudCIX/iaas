# libs
import serpy
# local
from .project import ProjectSerializer
from .virtual_router import VirtualRouterSerializer
from .vm import VMSerializer


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
    """
    project = ProjectSerializer()
    virtual_router = VirtualRouterSerializer()
    vms = VMSerializer(many=True)
