# libs
import serpy


class RouterSerializer(serpy.Serializer):
    """
    asset_tag:
        description: CloudCIX Asset Tag for the Router.
        type: integer
    capacity:
        description: |
            The capacity of the Router, indicating how many Virtual Routers can be placed on this Router.

            A null value means the Router has infinite capacity.
        type: integer
        nullable: true
    capacity_available:
        description: The space available on  the Router for Virtual Routers
        type: integer
    created:
        description: The date that the Router entry was created
        type: string
    credentials:
        description: The credentials for specified user on Router
        type: string
    enabled:
        description: Flag stating whether the Router is currently taking Virtual Routers.
        type: boolean
    id:
        description: The ID of the Router
        type: integer
    public_port_ips:
        description: List of IP Address for the public port on the Router.
        type: array
        items:
            type: string
    management_interface:
        description: Router's management interface name
        type: string
    management_ip:
        description: Router's management network IP used by Robot to access router.
        type: string
    model:
        description: The Juniper SRX Model of the router.
        type: string
    oob_interface:
        description: Router's oob interface name
        type: string
    private_interface:
        description: Router's private interface name
        type: string
    public_interface:
        description: Router's public interface name
        type: string
    region_id:
        description: The ID of the Region the Router is in.
        type: integer
    router_oob_interface:
        description: Router's router oob interface name
        type: string
    subnet_ids:
        description: List of Subnet IDs configured on the Router.
        type: array
        items:
            type: integer
    subnets:
        description: List of Subnet address ranges configured on the Router.
        type: array
        items:
            type: string
    updated:
        description: The date that the Router entry was last updated
        type: string
    uri:
        description: The absolute URL of the Router record that can be used to perform `Read`, `Update` and `Delete`.
        type: string
    username:
        description: username to be authenticated on Router
        type: string
    """
    asset_tag = serpy.Field()
    capacity = serpy.Field()
    capacity_available = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    credentials = serpy.Field()
    enabled = serpy.Field()
    id = serpy.Field()
    public_port_ips = serpy.Field(attr='get_public_port_ips', call=True)
    management_interface = serpy.Field()
    management_ip = serpy.Field()
    model = serpy.Field()
    oob_interface = serpy.Field()
    private_interface = serpy.Field()
    public_interface = serpy.Field()
    region_id = serpy.Field()
    router_oob_interface = serpy.Field()
    subnet_ids = serpy.Field(attr='get_subnet_ids', call=True)
    subnets = serpy.Field(attr='get_subnets', call=True)
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    username = serpy.Field()
