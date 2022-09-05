# libs
import serpy
# local
from iaas import state
from ..models import Router


class RouterMetricsSerializer(serpy.Serializer):
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
    enabled:
        description: Flag stating whether the Router is currently taking Virtual Routers.
        type: boolean
    id:
        description: The ID of the Router
        type: integer
    management_ip:
        description: Router's management network IP used by Robot to access router.
        type: string
    model:
        description: The Juniper SRX Model of the router.
        type: string
    region_id:
        description: The ID of the Region the Router is in.
        type: integer
    virtual_router_count:
        description: The number of virtual routers configured on the Router
        type: integer
    """
    asset_tag = serpy.Field()
    capacity = serpy.Field()
    enabled = serpy.Field()
    id = serpy.Field()
    management_ip = serpy.Field()
    model = serpy.Field()
    region_id = serpy.Field()
    virtual_router_count = serpy.MethodField()

    def get_virtual_router_count(self, obj: Router) -> int:
        """
        Get the number of currently running virtual routers on the Router instance
        """
        return obj.virtual_routers.exclude(state=state.CLOSED).count()
