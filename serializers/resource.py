# libs
import serpy
# local
from iaas.serializers.bom import BOMSerializer

__all__ = [
    'ResourceSerializer',
]


class ResourceSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the Resource record was created.
        type: string
    id:
        description: The ID of the Resource record
        type: integer
    name:
        description: The human-friendly name given to this Resource instance
        type: string
    parent_id:
        description: The id of the Resource that is controlling this Resource. Optional
        type: integer
    project_id:
        description: The id of the Project that this Resource belongs to
        type: integer
    resource_type:
        description: This defines what the Resource is and its functionality
        type: integer
    specs:
        description: The SKUs that are currently active on the Resource
        type: integer
    state:
        description: The current state of the Resource
        type: integer
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    name = serpy.Field()
    parent_id = serpy.Field()
    project_id = serpy.Field()
    resource_type = serpy.Field()
    specs = BOMSerializer(required=False, many=True)
    state = serpy.Field()
