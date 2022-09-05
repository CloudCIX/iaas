# libs
import serpy
# local
from .image import ImageSerializer
from .ip_address import IPAddressSerializer
from .project import ProjectSerializer
from .storage import StorageSerializer
from .subnet import SubnetSerializer
from .vm_history import VMHistorySerializer


__all__ = [
    'VMSerializer',
]


class VMSerializer(serpy.Serializer):
    """
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
        description: The Server this VM has been placed on.
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
    cpu = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    dns = serpy.Field()
    emails = serpy.Field(required=False)
    gateway_subnet = SubnetSerializer(required=False)
    guid = serpy.Field()
    history = VMHistorySerializer(many=True, attr='history.iterator', call=True)
    id = serpy.Field()
    image = ImageSerializer()
    ip_addresses = IPAddressSerializer(attr='vm_ips.iterator', call=True, many=True)
    name = serpy.Field()
    project = ProjectSerializer()
    public_key = serpy.Field(required=False)
    ram = serpy.Field()
    server_id = serpy.Field()
    stable = serpy.Field()
    storage_type = serpy.MethodField()
    storages = StorageSerializer(many=True, attr='storages.iterator', call=True)
    state = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    userdata = serpy.Field()

    def get_storage_type(self, obj):
        return getattr(obj, 'storage_type', None)
