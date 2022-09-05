# libs
import serpy
# local
from .interface import InterfaceSerializer
from .server_type import ServerTypeSerializer
from .storage_type import StorageTypeSerializer

__all__ = [
    'ServerSerializer',
]


class ServerSerializer(serpy.Serializer):
    """
    id:
        description: The ID of the Server record
        type: integer
    asset_tag:
        description: The CloudCIX asset tag of the server
        type: integer
    cores:
        description: Total number of physical cores in the Server
        type: integer
    created:
        description: The date that the Sever entry was created
        type: string
    enabled:
        description: Flag stating whether the host is currently taking VMs
        type: boolean
    gb:
        description: Total amount of space in the Server available for VMs
        type: integer
    hostname:
        description: The ip address and/or hostname of the Server
        type: string
    interfaces:
        description: The network interface in the Server
        type: array
        items:
            $ref: '#/components/schemas/Interface'
    model:
        description: Model name / number of the Server
        type: string
    ram:
        description: Total amount of RAM in the Server, in GB
        type: integer
    region_id:
        description: ID of the region the Server is a part of
        type: integer
    storage_type:
        $ref: '#/components/schemas/StorageType'
    type:
        $ref: '#/components/schemas/ServerType'
    updated:
        description: The date that the Server entry was last updated
        type: string
    uri:
        description: The absolute URL of the Server record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    vcpus:
        description: The total number of Virtual CPUs (vcpus) available for VMs on this server
        type: integer
    """
    asset_tag = serpy.Field()
    cores = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    enabled = serpy.Field()
    gb = serpy.Field()
    hostname = serpy.Field()
    id = serpy.Field()
    interfaces = InterfaceSerializer(many=True, attr='interfaces.iterator', call=True)
    model = serpy.Field()
    ram = serpy.Field()
    region_id = serpy.Field()
    storage_type = StorageTypeSerializer()
    type = ServerTypeSerializer()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    vcpus = serpy.Field()
