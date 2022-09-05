# libs
import serpy
# local
from .domain import DomainSerializer

__all__ = [
    'RecordSerializer',
]


class RecordSerializer(serpy.Serializer):
    """
    content:
        description: The DNS content of the Record.
        type: string
    created:
        description: Timestamp, in ISO format, of when this Record was created.
        type: string
    domain:
        $ref: '#/components/schemas/Domain'
    failover:
        description: Flag stating whether or not the Record is using failover.
        type: boolean
    failover_content:
        description: The DNS content to be used for the Record in failover cases.
        type: string
    id:
        description: The ID of the Record
        type: integer
    ip_address:
        description: The IP Address of the Record, for PTR Records.
        type: string
    member_id:
        type: integer
        description: The ID of the Member that owns the PTR Record. Non PTR Records will have this field as null
        nullable: true
    modified_by:
        description: The ID of the User that last updated the Record.
        type: integer
    name:
        description: The DNS name of the Record.
        type: string
    pk:
        description: The ID of the Record, both in iaas and in Rage4.
        type: integer
    priority:
        description: The priority value for this Record.
        type: integer
    time_to_live:
        description: The Time To Live (time_to_live) value for this DNS record.
        type: integer
    type:
        description: The type of this Record.
        type: string
    updated:
        description: Timestamp, in ISO format, of when this Record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the Record record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    content = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    domain = DomainSerializer(required=False)  # not required by PTR records
    failover = serpy.Field()
    failover_content = serpy.Field()
    id = serpy.Field()
    ip_address = serpy.Field()
    member_id = serpy.Field()
    modified_by = serpy.Field()
    name = serpy.Field()
    pk = serpy.Field()
    priority = serpy.Field()
    time_to_live = serpy.Field()
    type = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
