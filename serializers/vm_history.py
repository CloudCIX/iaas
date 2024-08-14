# libs
import serpy
from .storage_history import StorageHistorySerializer

__all__ = [
    'VMHistorySerializer',
]


class VMHistorySerializer(serpy.Serializer):
    """
    cpu_quantity:
        description: The quantity of the CPU for the VM.
        type: integer
    cpu_sku:
        description: The SKU for a CPU on a VM.
        type: string
    created:
        description: The date that the VM History entry was created
        type: string
    customer_address:
        description: The id of the address to be billed for the VM
        type: integer
    gpu_quantity:
        description: The quantity of the GPU for the VM.
        type: integer
    gpu_sku:
        description: The SKU for a GPU on a VM.
        type: string
    image_quantity:
        description: The quantity of an Image for the VM
        type: integer
    image_sku:
        description: The SKU for the Image of the VM.
        type: string
    modified_by:
        description: The users id of the user who checked the configuration.
        type: integer
    nat_quantity:
        description: The quantity of IP Addresses NATted on the VM.
        type: integer
    nat_sku:
        description: The SKU for NAT of a VM.
        type: string
    project_id:
        description: The id for the Project for the VM that has being changed.
        type: integer
    project_vm_name:
        description: The name of the Project and VM which can be used for billing purposes
        type: string
    ram_quantity:
        description: The quantity of the RAM for the VM.
        type: integer
    ram_sku:
        description: The SKU of the RAM for the VM.
        type: string
    state:
        description: The state for the VM.
        type: integer
    storages:
        description: An array of Storage History records created at the time this record was created.
        type: array
        items:
            $ref: '#/components/schemas/StorageHistory'
    storage_histories:
        description: An array of Storage History records created at the time this record was created.
        type: array
        items:
            $ref: '#/components/schemas/StorageHistory'

    vm_id:
        description: The id for the VM that has being changed.
        type: integer
    """
    cpu_quantity = serpy.Field(required=False)
    cpu_sku = serpy.Field(required=False)
    created = serpy.Field(attr='created.isoformat', call=True)
    customer_address = serpy.Field()
    gpu_quantity = serpy.Field(required=False)
    gpu_sku = serpy.Field(required=False)
    image_quantity = serpy.Field(required=False)
    image_sku = serpy.Field(required=False)
    modified_by = serpy.Field()
    nat_quantity = serpy.Field(required=False)
    nat_sku = serpy.Field(required=False)
    project_id = serpy.Field()
    project_vm_name = serpy.Field()
    ram_quantity = serpy.Field(required=False)
    ram_sku = serpy.Field(required=False)
    state = serpy.Field(required=False)
    storages = StorageHistorySerializer(attr='storage_histories.iterator', call=True, many=True)
    storage_histories = StorageHistorySerializer(attr='storage_histories.iterator', call=True, many=True)
    vm_id = serpy.Field()
