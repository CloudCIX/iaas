# libs
import serpy

__all__ = [
    'VPNHistorySerializer',
]


class VPNHistorySerializer(serpy.Serializer):
    """
    created:
        description: The date that the VPN History entry was created
        type: string
    customer_address:
        description: The address id of the customer to be billed.
        type: integer
    modified_by:
        description: The users id of the user who checked the configuration.
        type: integer
    project_name:
        description: The name of the project when the VPN History record was created.
        type: integer
    vpn_id:
        description: The id for the vm that has being changed.
        type: integer
    vpn_quantity:
        description: The quantity of the sku for the VPN
        type: integer
    vpn_sku:
        description: The SKU for the VPN.
        type: string
    """

    created = serpy.Field(attr='created.isoformat', call=True)
    customer_address = serpy.Field()
    modified_by = serpy.Field()
    project_name = serpy.Field()
    vpn_id = serpy.Field()
    vpn_quantity = serpy.Field()
    vpn_sku = serpy.Field()
