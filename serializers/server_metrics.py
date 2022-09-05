# libs
import serpy

__all__ = [
    'ServerMetricsSerializer',
]


class ServerMetricsSerializer(serpy.Serializer):
    """
    asset_tag:
        description: The CloudCIX asset tag of the server
        type: integer
    enabled:
        description: Flag stating whether the host is currently taking VMs
        type: boolean
    gb:
        description: Total amount of space in the Server available for VMs
        type: integer
    gb_in_use:
        description: Total amount of disk space in use by VMs on this Server
        type: integer
    hostname:
        description: The ip address and/or hostname of the Server
        type: string
    id:
        description: The ID of the Server record
        type: integer
    model:
        description: Model name / number of the Server
        type: string
    ram:
        description: Total amount of RAM in the Server, in GB
        type: integer
    ram_in_use:
        description: Total amount of RAM in use by VMs on this Server
        type: integer
    region_id:
        description: ID of the region the Server is a part of
        type: integer
    storage_type:
        description: The name of the Storage Type that this Server uses (i.e. "SSD")
        type: string
    type:
        description: The name of the OS that this Server uses (i.e. "HyperV")
        type: string
    vcpus:
        description: The total number of Virtual CPUs (vcpus) available for VMs on this server
        type: integer
    vcpus_in_use:
        description: Total amount of vcpus in use by VMs on this Server
        type: integer
    """
    asset_tag = serpy.Field()
    enabled = serpy.Field()
    gb = serpy.Field()
    gb_in_use = serpy.Field()
    hostname = serpy.Field()
    id = serpy.Field()
    model = serpy.Field()
    ram = serpy.Field()
    ram_in_use = serpy.Field()
    region_id = serpy.Field()
    storage_type = serpy.Field(attr='storage_type.name')
    type = serpy.Field(attr='type.name')
    vcpus = serpy.Field()
    vcpus_in_use = serpy.Field()
