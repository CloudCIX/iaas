# libs
import serpy
# local
from .asn import ASNSerializer

__all__ = [
    'AllocationSerializer',
]


class AllocationSerializer(serpy.Serializer):
    """
    address_id:
        description: The ID of the Address that the Allocation is allocated to
        type: integer
    address_range:
        description: The address range for the Allocation in CIDR format
        type: string
    asn:
        $ref: '#/components/schemas/ASN'
    created:
        description: Timestamp, in ISO format, of when the Allocation record was created.
        type: string
    id:
        description: The ID of the Allocation record
        type: integer
    modified_by:
        description: The ID of the User who last made changes to the Allocation
        type: integer
    name:
        description: The name of the Allocation record
        type: string
    subnets_in_use:
        description: The total number of Subnets that are in use in this Allocation
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Allocation record was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the Allocation record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """
    address_id = serpy.Field()
    address_range = serpy.Field()
    asn = ASNSerializer()
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    modified_by = serpy.Field()
    name = serpy.Field()
    subnets_in_use = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
