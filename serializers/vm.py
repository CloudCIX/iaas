# libs
import serpy
# local
from .image import ImageSerializer
from .ip_address import IPAddressSerializer
from .project import ProjectSerializer
from .storage import StorageSerializer
from .subnet import SubnetSerializer
from .vm_history import VMHistorySerializer
from iaas.models.vm import VM


__all__ = [
    'BaseVMSerializer',
    'VMSerializer',
]


class BaseVMSerializer(serpy.Serializer):
    """
    available_devices:
        description: |
            The number of devices curently available to be assigned to VM. None will be returned it the VMs server does
            not have any devices.
        type: integer
    cpu:
        description: The number of cpu cores allocated for the VM.
        type: integer
    created:
        description: The date that the VM entry was created
        type: string
    dns:
        description: The DNS for the VM.
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified vm configuration.
        type: array
        items:
            description: email address
            type: string
    gpu:
        description: The number of GPU devices allocated for the VM.
        type: integer
    guid:
        description: GUID of the VM which will be used as part of the URL path for the VM's cloud-init files
        type: string
    id:
        description: The id given for the VM.
        type: integer
    image_id:
        description: The ID of the Image for this VM.
        type: integer
    name:
        description: The name given to the vm.
        type: string
    public_key:
        description: |
            The public key added to VM during build process to enable ssh access from machine with corresponding
            private key.
        type: string
    ram:
        description: The number of ram allocated for the VM.
        type: integer
    server_id:
        description: The ID of the Server this VM has been placed on.
        type: integer
    stable:
        description: |
            A flag stating whether or not the VM is classified as stable.
            A VM is classified as stable when it and it's snapshots are in a stable state e.g. Running, Quiesced or
            Scrubbed.
        type: boolean
    state:
        description: The state that the VM is currently in.
        type: integer
    updated:
        description: The date that the VM entry was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the VM instance.
        type: string
        format: url
    userdata:
        description: Configuration file to be used by Cloud Init
        type: string
    """
    available_devices = serpy.Field()
    cpu = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    dns = serpy.Field()
    emails = serpy.Field(required=False)
    gpu = serpy.Field()
    guid = serpy.Field()
    id = serpy.Field()
    image_id = serpy.Field()
    name = serpy.Field()
    public_key = serpy.Field(required=False)
    ram = serpy.Field()
    server_id = serpy.Field()
    stable = serpy.Field()
    state = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    userdata = serpy.Field()


class VMSerializer(BaseVMSerializer):
    """
    available_devices:
        description: |
            The number of devices curently available to be assigned to VM. None will be returned it the VMs server does
            not have any devices.
        type: integer
    cpu:
        description: The number of cpu cores allocated for the VM.
        type: integer
    created:
        description: The date that the VM entry was created
        type: string
    dns:
        description: The DNS for the VM.
        type: string
    emails:
        description: Email addresses of the Project owner and user who modified vm configuration.
        type: array
        items:
            description: email address
            type: string
    gateway_subnet:
        $ref: '#/components/schemas/Subnet'
    gpu:
        description: The number of GPU devices allocated for the VM.
        type: integer
    guid:
        description: GUID of the VM which will be used as part of the URL path for the VM's cloud-init files
        type: string
    history:
        description:
        $ref: '#/components/schemas/VMHistory'
    id:
        description: The id given for the VM.
        type: integer
    image:
        $ref: '#/components/schemas/Image'
    image_id:
        description: The ID of the Image for this VM.
        type: integer
    ip_addresses:
        description: A list of private IP Address objects, containing a public ip if one exists
        type: array
        items:
            description: Private IP Address
            $ref: '#/components/schemas/IPAddress'
    name:
        description: The name given to the vm.
        type: string
    project:
        description: The Project this VM is a part of.
        $ref: '#/components/schemas/Project'
    public_key:
        description: |
            The public key added to VM during build process to enable ssh access from machine with corresponding
            private key.
        type: string
    ram:
        description: The number of ram allocated for the VM.
        type: integer
    server_id:
        description: The ID of the Server this VM has been placed on.
        type: integer
    stable:
        description: |
            A flag stating whether or not the VM is classified as stable.
            A VM is classified as stable when it and it's snapshots are in a stable state e.g. Running, Quiesced or
            Scrubbed.
        type: boolean
    state:
        description: The state that the VM is currently in.
        type: integer
    storage_type:
        description: |
            The name of the Storage Type of the VM. This optional and will only be returned for resource requests
        type: string
    storages:
        description: The Storages used for the VM.
        type: array
        items:
            $ref: '#/components/schemas/Storage'
    updated:
        description: The date that the VM entry was last updated
        type: string
    uri:
        description: URL that can be used to run methods in the API associated with the VM instance.
        type: string
        format: url
    userdata:
        description: Configuration file to be used by Cloud Init
        type: string
    """
    gateway_subnet = SubnetSerializer(required=False)
    history = VMHistorySerializer(many=True, attr='history.iterator', call=True)
    image = ImageSerializer()
    ip_addresses = IPAddressSerializer(attr='vm_ips.iterator', call=True, many=True)
    project = ProjectSerializer()
    storage_type = serpy.MethodField()
    storages = StorageSerializer(many=True, attr='storages.iterator', call=True)

    def get_storage_type(self, obj: VM):
        return getattr(obj, 'storage_type', None)
