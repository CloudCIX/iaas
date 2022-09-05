# libs
import serpy
# local

__all__ = [
    'MetricsSerializer',
]


class MetricsSerializer(serpy.Serializer):
    """
    routers:
        description: Metrics of the routers in the chosen region
        type: array
        items:
            $ref: '#/components/schemas/RouterMetrics'
    servers:
        description: Metrics of the servers in the chosen region
        type: array
        items:
            $ref: '#/components/schemas/ServerMetrics'
    subnets:
        description: Metrics of the Subnets for the chosen region
        type: array
        items:
            type: object
            properties:
                address_range:
                    description: The address range of the subnet
                    type: string
                capacity:
                    description: The amount of IP Addresses that can be created in the Subnet
                    type: integer
                id:
                    description: The ID of the Subnet
                    type: integer
                ips_in_use:
                    description: The amount of IP Addresses currently in use in the Subnet
                    type: integer
                name:
                    description: The name given to the Subnet
                    type: string
    vms:
        description: Metrics of the vms in the chosen region, broken up by state and server
        type: array
        items:
            type: object
            properties:
                state:
                    description: the state of the vms
                    type: integer
                server_id:
                    description: the id of the server the vms are on
                    type: integer
                count:
                    description: the number of vms that match the state and server_id parameters
                    type: integer
    """
    routers = serpy.Field()
    servers = serpy.Field()
    subnets = serpy.Field()
    vms = serpy.Field()
