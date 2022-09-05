# libs
import serpy
# local
from .snapshot_history import SnapshotHistorySerializer
from .vm import VMSerializer

__all__ = [
    'SnapshotSerializer',
    'SnapshotTreeSerializer',
]


class SnapshotSerializer(serpy.Serializer):
    """
    active:
        description: The snapshot the associated VM currently runs from
        type: boolean
    created:
        description: The date that the Snapshot record was created
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified snapshot configuration.
        type: array
        items:
            description: email address
            type: string
    history:
        description:
        $ref: '#/components/schemas/SnapshotHistory'
    id:
        description: The ID of the Snapshot record
        type: integer
    name:
        description: The name of the Snapshot
        type: string
    parent_id:
        description: The parent of this Snapshot
        type: integer
    remove_subtree:
        description: |
            Used when removing snapshots. During removal, if True, then snapshot children are also removed.
            If there is a more than one line, they should be in line with the first, not indented further.
        type: boolean
    state:
        description: The state that the Snapshot is currently in.
        type: integer
    updated:
        description: The date the Snapshot record was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the Snapshot instance.
        type: string
        format: url
    vm:
        $ref: '#/components/schemas/VM'

    """
    active = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    emails = serpy.Field(required=False)
    history = SnapshotHistorySerializer(many=True, attr='history.iterator', call=True)
    id = serpy.Field()
    name = serpy.Field()
    parent_id = serpy.Field()
    remove_subtree = serpy.Field()
    state = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    vm = VMSerializer()


class SnapshotTreeSerializer(serpy.Serializer):
    """
    active:
        description: The snapshot the associated VM currently runs from
        type: boolean
    children:
        description: A list of Snapshots to which this Snapshot is the parent - TODO fix serializing self in docgen
        type: integer
    created:
        description: The date that the Snapshot record was created
        type: string
    history:
        description:
        $ref: '#/components/schemas/SnapshotHistory'
    id:
        description: The ID of the Snapshot record
        type: integer
    name:
        description: The name of the Snapshot
        type: string
    remove_subtree:
        description: |
            Used when removing snapshots. During removal, if True, then snapshot children are also removed.
            If there is a more than one line, they should be in line with the first, not indented further.
        type: boolean
    state:
        description: The state that the Snapshot is currently in.
        type: integer
    updated:
        description: The date the Snapshot record was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the Snapshot instance.
        type: string
        format: url
    """

    active = serpy.Field()
    children = serpy.Field(attr='get_children', call=True, required=False)
    created = serpy.Field(attr='created.isoformat', call=True)
    history = SnapshotHistorySerializer(many=True, attr='history.iterator', call=True)
    id = serpy.Field()
    name = serpy.Field()
    remove_subtree = serpy.Field()
    state = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
