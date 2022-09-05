# libs
import serpy

__all__ = [
    'SnapshotHistorySerializer',
]


class SnapshotHistorySerializer(serpy.Serializer):
    """
    created:
        description: The date that the Snapshot History entry was created
        type: string
    customer_address:
        description: The address id of the customer to be billed.
        type: integer
    modified_by:
        description: The users id of the user who modified the Snapshot.
        type: integer
    project_id:
        description: The id for the Project for the Snapshot that has being changed.
        type: integer
    snapshot_id:
        description: The id for the snapshot that has being changed.
        type: integer
    state:
        description: The state for the Snapshot.
        type: integer
    vm_id:
        description: The id for the VM for the Snapshot that has being changed.
        type: integer
    """

    created = serpy.Field(attr='created.isoformat', call=True)
    customer_address = serpy.Field()
    modified_by = serpy.Field()
    project_id = serpy.Field()
    snapshot_id = serpy.Field()
    state = serpy.Field()
    vm_id = serpy.Field()
