# libs
import serpy

__all__ = [
    'BackupHistorySerializer',
]


class BackupHistorySerializer(serpy.Serializer):
    """
    backup_id:
        description: The id for the Backup that has being changed.
        type: integer
    created:
        description: The date that the Backup History entry was created
        type: string
    customer_address:
        description: The address id of the customer to be billed.
        type: integer
    modified_by:
        description: The users id of the user who modified the Backup.
        type: integer
    project_id:
        description: The id for the Project for the Backup that has being changed.
        type: integer
    state:
        description: The state for the Backup.
        type: integer
    vm_id:
        description: The id for the VM for the Backup is of.
        type: integer
    """

    backup_id = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    customer_address = serpy.Field()
    modified_by = serpy.Field()
    project_id = serpy.Field()
    state = serpy.Field()
    vm_id = serpy.Field()
