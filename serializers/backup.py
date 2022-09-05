# libs
import serpy
# local
from .backup_history import BackupHistorySerializer
from .vm import VMSerializer

__all__ = [
    'BackupSerializer',
]


class BackupSerializer(serpy.Serializer):
    """
    created:
        description: The date that the backup record was created
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified the backup.
        type: array
        items:
            description: email address
            type: string
    history:
        description:
        $ref: '#/components/schemas/BackupHistory'
    id:
        description: The ID of the backup record
        type: integer
    name:
        description: The name of the Backup
        type: string
    repository:
        description: |
            Which repository is used for backup.
            repository = 1, primary storage.
            repository = 2, secondary storage.
        type: integer
    state:
        description: The state that the backup is currently in.
        type: integer
    time_valid:
        description: The time from which the backup is valid.
        type: string
    updated:
        description: The date the backup record was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the Backup instance.
        type: string
        format: url
    vm:
        $ref: '#/components/schemas/VM'

    """
    created = serpy.Field(attr='created.isoformat', call=True)
    emails = serpy.Field(required=False)
    history = BackupHistorySerializer(many=True, attr='history.iterator', call=True)
    id = serpy.Field()
    name = serpy.Field()
    repository = serpy.Field()
    state = serpy.Field()
    time_valid = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    vm = VMSerializer()
