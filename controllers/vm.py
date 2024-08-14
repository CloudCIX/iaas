# stdlib
from datetime import datetime
import json
import logging
from collections import deque
from typing import Any, Deque, Dict, List, Optional
# libs
import netaddr
from cloudcix_rest.controllers import ControllerBase
from cloudcix_rest.utils import get_error_details
from django.conf import settings
from django.core import mail
from sshpubkeys import SSHKey
from sshpubkeys.exceptions import InvalidKeyError
# local
from . import helpers
from .storage import StorageCreateController, StorageUpdateController
from iaas.models import (
    ASN,
    Device,
    Image,
    IPAddress,
    Project,
    RegionImage,
    Server,
    Storage,
    StorageType,
    Subnet,
    VirtualRouter,
    VM,
)
import iaas.skus as skus
import iaas.state as states


__all__ = [
    'VMCreateController',
    'VMUpdateController',
    'VMListController',
]

WINDOWS_PRIMARY_DRIVE_MINIMUM = 32
UPDATE_STATES = {states.RUNNING_UPDATE, states.QUIESCED_UPDATE}
CLOUD_INIT_HEADERS = ['#!', '#include', '#cloud-config', '#upstart-job', '#cloud-boothook']


class VMListController(ControllerBase):
    """
    Validates User data used to filter a list of VMs
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more
        specific for this Controller
        """
        allowed_ordering = (
            'created',
            'name',
            'project_id',
            'state',
            'updated',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'image__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'project_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'project__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'project__region_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'server_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'server__type_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'server__type__name': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'state': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'updated': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class VMCreateController(ControllerBase):
    """
    Validates User data used to create a VM
    """
    capacity = 0
    vm_history: Dict[str, Any] = {}
    windows_os = False

    class Meta(ControllerBase.Meta):
        """
        Override ControllerBase.Meta fields
        """
        model = VM
        validation_order = (
            'project_id',
            'image_id',
            'storage_type_id',
            'storages',
            'cpu',
            'ram',
            'server',
            'dns',
            'name',
            'public_key',
            'gateway_subnet',
            'ip_addresses',
            'userdata',
        )

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        Extra handling of the errors property for handling the storages errors in the case its a list
        """
        popped = False
        storage_errors = self._errors.get('storages', None)
        if isinstance(storage_errors, list):
            # Remove it, call super and add it back in
            storage_errors = self._errors.pop('storages')
            popped = True
        errors = super(VMCreateController, self).errors
        if popped:
            errors['storages'] = storage_errors
        return errors

    def validate_project_id(self, project_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the User's Project into which this new VM should be added.
        type: integer
        """
        if project_id is None:
            return 'iaas_vm_create_101'

        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            return 'iaas_vm_create_102'

        try:
            proj = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return 'iaas_vm_create_103'

        if proj.address_id != self.request.user.address['id']:
            return 'iaas_vm_create_104'

        self.cleaned_data['project'] = proj
        return None

    def validate_image_id(self, image_id: Optional[int]) -> Optional[str]:
        """
        description: The ID of the Image that will be used to build the VM.
        type: integer
        """
        if image_id is None:
            return 'iaas_vm_create_105'

        try:
            image_id = int(image_id)
        except (ValueError, TypeError):
            return 'iaas_vm_create_106'

        try:
            image = Image.objects.get(pk=image_id, public=True)
        except Image.DoesNotExist:
            return 'iaas_vm_create_107'

        # Can't go any further without the Project
        if 'project' not in self.cleaned_data:
            return None

        try:
            RegionImage.objects.get(image=image, region=self.cleaned_data['project'].region_id)
        except RegionImage.DoesNotExist:
            return 'iaas_vm_create_108'

        self.vm_history['image_quantity'] = 1
        if image_id in skus.IMAGE_SKU_MAP:
            self.vm_history['image_sku'] = skus.IMAGE_SKU_MAP[image_id]
            if skus.IMAGE_SKU_MAP[image_id].startswith('MSServer'):
                self.windows_os = True
        else:
            self.vm_history['image_sku'] = skus.DEFAULT

        self.cleaned_data['image'] = image
        return None

    def validate_storage_type_id(self, storage_type_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The ID of the StorageType that will be used in the VM
        type: integer
        """
        if storage_type_id is None:
            return 'iaas_vm_create_109'

        try:
            storage_type_id = int(storage_type_id)
        except (ValueError, TypeError):
            return 'iaas_vm_create_110'

        try:
            storage_type = StorageType.objects.get(pk=storage_type_id)
        except StorageType.DoesNotExist:
            return 'iaas_vm_create_111'

        if storage_type_id in skus.STORAGE_SKU_MAP:
            self.vm_history['storage_type_sku'] = skus.STORAGE_SKU_MAP[storage_type_id]
        else:
            self.vm_history['storage_type_sku'] = skus.DEFAULT
        self.cleaned_data['storage_type'] = storage_type
        return None

    def validate_storages(self, storages: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of StorageCreate objects to create the initial Storage objects for the VM.
        type: array
        items:
            $ref: '#/components/schemas/StorageCreate'
        """
        storages = storages or []
        if not isinstance(storages, list):
            return 'iaas_vm_create_112'

        if len(storages) == 0:
            return 'iaas_vm_create_113'

        # Create each of the storage instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(storages))]
        instances: Deque[Storage] = deque()
        primary = 0
        windows_primary_drive_size = 0

        for index, storage in enumerate(storages):
            if not isinstance(storage, dict):
                details = get_error_details('iaas_vm_create_114')
                errors[index] = details['iaas_vm_create_114']
                continue

            controller = StorageCreateController(data=storage, request=self.request, span=self.span)

            # Validate the controller
            if not controller.is_valid():
                # If the controller isn't valid, add the errors to the list
                errors[index] = controller.errors
                continue

            # Check if the storage is primary
            if controller.cleaned_data['primary']:
                primary += 1
                if self.windows_os:
                    windows_primary_drive_size = controller.cleaned_data['gb']

            # Add the instance to the instances deque
            instances.append(controller.instance)

            # Add to the capacity to the amount maintained
            self.capacity += controller.instance.gb

        # Check if any storage item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['storages'] = errors
            return None

        # If we don't have exactly 1 primary storage object, then this is also an error
        if primary != 1:
            details = get_error_details('iaas_vm_create_115')
            self._errors['storages'] = [details['iaas_vm_create_115']] * len(storages)
            return None

        if self.windows_os and windows_primary_drive_size < WINDOWS_PRIMARY_DRIVE_MINIMUM:
            return 'iaas_vm_create_116'

        # If we make it here, then everything is fine
        self.cleaned_data['storages'] = instances
        return None

    def validate_cpu(self, cpu: Optional[int]) -> Optional[str]:
        """
        description: |
            The number of Virtual CPUs (vCPUs) that the VM should be created with.
        type: integer
        minimum: 1
        maximum: 24
        """
        if cpu is None:
            return 'iaas_vm_create_117'

        try:
            cpu = int(cpu)
        except (ValueError, TypeError):
            return 'iaas_vm_create_118'

        if cpu <= 0:
            return 'iaas_vm_create_119'

        self.vm_history['cpu_quantity'] = cpu
        self.vm_history['cpu_sku'] = skus.VCPU_001

        self.cleaned_data['cpu'] = cpu
        return None

    def validate_ram(self, ram: Optional[int]) -> Optional[str]:
        """
        description: |
            The amount of RAM (in GB) that the VM should be created with.
        type: integer
        minimum: 1
        maximum: 128
        """
        if ram is None:
            return 'iaas_vm_create_120'

        try:
            ram = int(ram)
        except (ValueError, TypeError):
            return 'iaas_vm_create_121'

        if ram <= 0:
            return 'iaas_vm_create_122'

        self.vm_history['ram_quantity'] = ram
        self.vm_history['ram_sku'] = skus.RAM_001

        self.cleaned_data['ram'] = ram
        return None

    def validate_server(self, server: Optional[str]) -> Optional[str]:
        """
        description: |
            Determine which Server in the region will host the new VM.
        generative: true
        """
        required = ['project', 'image', 'storage_type', 'storages', 'cpu', 'ram']
        for field in required:
            if field not in self.cleaned_data:
                # If we're missing a key, return because we can't validate this.
                return None

        # Get all the Servers of the required type in the region with the right storage type and are enabled
        storage_type = self.cleaned_data.pop('storage_type')
        region_id = self.cleaned_data['project'].region_id
        servers = Server.objects.filter(
            region_id=region_id,
            type=self.cleaned_data['image'].server_type,
            enabled=True,
            storage_type=storage_type,
        )

        # Construct the requirement vector for this VM
        requirement_vector = [self.cleaned_data['ram'], self.capacity, self.cleaned_data['cpu']]

        # Find the best Server for this VM
        found_server = None
        max_suitability = float('-inf')
        for s in servers:
            suitability = s.get_suitability(requirement_vector)
            if suitability > max_suitability:
                found_server = s
                max_suitability = suitability

        if found_server is None:
            # Servers full? Let's send an email!
            data = json.dumps(self.data, indent=2)
            logger = logging.getLogger('iaas.controllers.vm.validate_server')
            pod_name = settings.POD_NAME
            organization_url = settings.ORGANIZATION_URL
            user_details = f'{self.request.user.first_name} {self.request.user.surname} ({self.request.user.email})'
            logger.error(
                f'Region #{region_id} located no servers for the following VM.\n{data}. This was requested by '
                f'{user_details} in  {self.request.user.address["name"]}.',
            )
            if not settings.TESTING:  # pragma: no cover
                msg = f'iaas.{pod_name}.{organization_url} was unable to find a Server in Region #{region_id}.\n'
                msg += f'{user_details} in {self.request.user.address["name"]} requsted to build:'
                msg += f'\n\tCPU: {self.cleaned_data["cpu"]} \n\tRAM: {self.cleaned_data["ram"]}'
                msg += f'\n\tStorage: {self.capacity}GB {storage_type.name}'
                msg += f'\n\tServer Type: {self.cleaned_data["image"].server_type.name}'
                try:
                    mail.send_mail(
                        f'Region #{region_id} found no servers for a VM.\n',
                        msg,
                        'notifications@cloudcix.com',
                        ['developers@cloudcix.com', 'noc@cix.ie'],
                    )
                    # TODO: Emails in above mail needs to come from settings files
                except Exception:
                    logger.error(
                        f'Unable to send email for Region #{region_id} from iaas.{pod_name}.{organization_url}.',
                        exc_info=True,
                    )
            return 'iaas_vm_create_123'

        self.cleaned_data['server'] = found_server
        return None

    def validate_dns(self, dns: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing IP Addresses, separated by commas, that represent the DNS servers that the VM will use.
        type: string
        """
        if dns is None:
            return 'iaas_vm_create_124'

        servers = dns.split(',')
        for server in servers:
            try:
                netaddr.IPAddress(server.strip())
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_vm_create_125'

        self.cleaned_data['dns'] = ','.join(entry.strip() for entry in servers)
        return None

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            A verbose name for the VM. Must be unique within a Project.
        type: string
        """
        if name is None:
            name = ''
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_vm_create_126'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_vm_create_127'

        # Can't go any further without the Project
        if 'project' not in self.cleaned_data:
            return None

        if VM.objects.filter(project=self.cleaned_data['project'], name=name).exclude(state=states.CLOSED).exists():
            return 'iaas_vm_create_128'

        self.cleaned_data['name'] = name
        return None

    def validate_public_key(self, public_key: Optional[str]) -> Optional[str]:
        """
        description: |
            A public key that will be added to the VM during build to enable ssh access from machine with corresponding
            private key.
        type: string
        required: false
        """
        if public_key is not None:
            try:
                ssh = SSHKey(public_key, strict=True)
                ssh.parse()
            except (InvalidKeyError, NotImplementedError):
                return 'iaas_vm_create_129'
            self.cleaned_data['public_key'] = public_key
        return None

    def validate_gateway_subnet(self, gateway_subnet: Optional[str]) -> Optional[str]:
        """
        description: |
            The address range of the Subnet that will be used as the gateway subnet for the VM. Only IP's from this
            subnet can be NATed to a public IP address.
        type: string
        """
        if gateway_subnet is None:
            gateway_subnet = ''

        try:
            gateway_subnet = netaddr.IPNetwork(gateway_subnet)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            return 'iaas_vm_create_130'

        if 'project' not in self.cleaned_data:
            return None

        try:
            subnet = Subnet.objects.get(
                deleted__isnull=True,
                address_range=str(gateway_subnet),
                address_id=self.request.user.address['id'],
                allocation__asn__number=self.cleaned_data['project'].pk + ASN.pseudo_asn_offset,
            )
        except Subnet.DoesNotExist:
            return 'iaas_vm_create_131'

        self.cleaned_data['gateway_subnet'] = subnet
        return None

    def validate_ip_addresses(self, ip_addresses: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            Validate list of dictionaries sent in the format of: 'ip_addresses':[{'address': '1.1.1.1', 'nat': True}].
            `address` is a private ip address from one of the subnets on the vm's project's virtual_router.
            Only an `address` from the `gateway_subnet` can be `nat`: True
        type: List[Dict[str, Any]]
        """
        ip_addresses = ip_addresses or []

        if not isinstance(ip_addresses, list):
            return 'iaas_vm_create_132'

        if len(ip_addresses) == 0:
            return 'iaas_vm_create_133'

        ips = set()
        for ip in ip_addresses:
            ips.add(ip['address'])

        if len(ips) != len(ip_addresses):
            return 'iaas_vm_create_134'

        if 'project' not in self.cleaned_data or 'image' not in self.cleaned_data:
            return None

        image = self.cleaned_data['image']
        if len(ip_addresses) > 1 and not image.multiple_ips:
            return 'iaas_vm_create_135'

        gateway_subnet = None
        if 'gateway_subnet' in self.cleaned_data:
            gateway_subnet = netaddr.IPNetwork(self.cleaned_data['gateway_subnet'].address_range)

        # Get a list of valid subnets on the projects virtual_router
        virtual_router = VirtualRouter.objects.get(project=self.cleaned_data['project'].pk)

        subnets = Subnet.objects.filter(virtual_router_id=virtual_router.pk)

        region_subnet = virtual_router.ip_address.subnet

        nat_quantity = 0

        to_delete: Deque[IPAddress] = deque()
        for ip in ip_addresses:
            nat = ip.pop('nat', False)
            try:
                address = netaddr.IPAddress(ip['address'])
            except (TypeError, ValueError, netaddr.AddrFormatError):
                return 'iaas_vm_create_136'

            if address.is_ipv4_private_use() is False:
                return 'iaas_vm_create_137'

            for subnet in subnets:
                subnet_network = netaddr.IPNetwork(subnet.address_range)
                if address not in subnet_network:
                    continue

                if address in ([
                    subnet_network.network,     # Network Address
                    subnet_network.broadcast,   # Broadcast Address
                    subnet_network.ip,          # Gateway Address
                ]):
                    return 'iaas_vm_create_138'

                # Check that address does not overlap with another ip in subnet
                existing = subnet.ip_addresses.values_list('address', flat=True)

                existing = netaddr.IPSet(existing)
                if address in existing:
                    return 'iaas_vm_create_139'

                ip['subnet'] = subnet

                break

            if 'subnet' not in ip:
                return 'iaas_vm_create_140'

            # Check if IP is in gateway subnet and can be NATed
            if nat:
                if gateway_subnet is None or ip['address'] not in gateway_subnet:
                    return 'iaas_vm_create_141'

            # If any errors have occurred we are not going to create any fips
            if len(self._errors) > 0:
                return None

            ip['public_ip'] = None
            if nat:
                nat_quantity += 1
                try:
                    public_ip = helpers.create_public_ip(self.request, region_subnet, 'iaas_vm_create_142', self.span)
                    ip['public_ip'] = public_ip
                    to_delete.append(public_ip)
                except helpers.IAASException as e:  # pragma: no cover
                    for public_ip in to_delete:
                        public_ip.delete()
                    return e.args[0]

        self.cleaned_data['ip_addresses'] = ip_addresses
        self.vm_history['nat_quantity'] = nat_quantity
        self.vm_history['nat_sku'] = skus.NAT_001

        return None

    def validate_userdata(self, userdata: Optional[str]) -> Optional[str]:
        """
        description: |
            Cloud Init allows Mime Multi-part messages, or files that start with a given set of strings
        type: str
        """
        if userdata is None:
            return None

        # Check if the OS image supports Cloud Init
        if 'image' not in self.cleaned_data:
            return None
        image = self.cleaned_data['image']
        if not image.cloud_init:
            return 'iaas_vm_create_143'

        userdata = str(userdata).strip()
        if len(userdata) > self.get_field('userdata').max_length:
            return 'iaas_vm_create_144'

        valid = False
        for header in CLOUD_INIT_HEADERS:
            if userdata.startswith(header):
                valid = True
                break

        if not valid:
            # Check if it's a Mime Multi-part file
            if '\nMIME-Version: ' not in userdata:
                return 'iaas_vm_create_145'

        self.cleaned_data['userdata'] = userdata
        return None


class VMUpdateController(ControllerBase):
    """
    Validates VM data used to update a VM
    """
    update_virtual_router = False
    close_vm = False

    create_vm_history = False

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields
        """
        model = VM
        validation_order = (
            'name',
            'state',
            'ip_addresses',
            'cpu',
            'ram',
            'storages',
            'userdata',
            'gpu',
        )

    @property
    def errors(self) -> Dict[str, Dict[str, Any]]:
        """
        Extra handling of the errors property for handling the storages errors in the case its a list
        """
        popped = False
        storage_errors = self._errors.get('storages', None)
        if isinstance(storage_errors, list):
            # Remove it, call super and add it back in
            storage_errors = self._errors.pop('storages')
            popped = True
        errors = super(VMUpdateController, self).errors
        if popped:
            errors['storages'] = storage_errors
        return errors

    def validate_name(self, name: Optional[str]) -> Optional[str]:
        """
        description: |
            A verbose name for the VM. Must be unique within a Project.
        type: string
        """
        if name is None:
            name = self._instance.name
        name = str(name).strip()

        if len(name) == 0:
            return 'iaas_vm_update_101'

        if len(name) > self.get_field('name').max_length:
            return 'iaas_vm_update_102'

        if VM.objects.filter(
            project=self._instance.project,
            name=name,
        ).exclude(pk=self._instance.pk).exclude(state=states.CLOSED).exists():
            return 'iaas_vm_update_103'

        self.cleaned_data['name'] = name
        return None

    def validate_state(self, state: Optional[int]) -> Optional[str]:
        """
        description: |
            Change the state of the VM, causing the CloudCIX Robot to perform requested actions on it.

            There is a specific set of states from which the user can request a change, and each of these allowed states
            has a subset of states it can be changed to. These are as follows;

            - RUNNING (4)     -> QUIESCE (5), or UPDATE (10)
            - QUIESCED (6)    -> RESTART (7), SCRUB (8) , or UPDATE (10)
            - SCRUB_QUEUE (9) -> QUIESCED (6), or RESTART (7)
        type: integer
        """
        if state is None:
            return None

        try:
            state = int(state)
        except (ValueError, TypeError):
            return 'iaas_vm_update_104'

        # Ignore if we're not changing the state
        if state == self._instance.state:
            return None

        # Ensure the sent state is in the valid range
        if state not in states.VALID_RANGE:
            return 'iaas_vm_update_105'

        # Determine which state map to use for this request
        if self.request.user.robot:
            available_states = states.ROBOT_STATE_MAP
        else:
            available_states = states.USER_STATE_MAP

        # Ensure current state is in chosen map.
        if self._instance.state not in available_states:
            return 'iaas_vm_update_106'

        # Ensure sent state is a valid state change.
        if state not in available_states[self._instance.state]:
            return 'iaas_vm_update_107'

        # If the requesteed state is the SCRUB VM, ensure
        # 1. There are no GPUs attached
        # 2. If any snapshots, they are all in a closed state
        if state == states.SCRUB:
            if self._instance.gpu > 0:
                return 'iaas_vm_update_108'
            if self._instance.snapshots.exclude(state=states.CLOSED).exists():
                return 'iaas_vm_update_109'

        if state == states.CLOSED:
            self.close_vm = True
            if IPAddress.objects.filter(vm=self._instance.pk, public_ip_id__isnull=False).exists():
                self.update_virtual_router = True

        if not self._instance.snapshots_stable():
            return 'iaas_vm_update_110'

        self._create_history()

        self.vm_history['state'] = state
        self.cleaned_data['state'] = state
        return None

    def validate_ip_addresses(self, ip_addresses: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            Validate list of dictionaries sent in the format of: 'ip_addresses':[{'address': 1.1.1.1, 'nat': True}].
            `address` is a private ip address from one of the subnets on the vm's project's virtual_router.
            Only an `address` from the `gateway_subnet` can be `nat`: True

        type: List[Dict[str, Any]]
        """
        ip_addresses = ip_addresses or []

        if not isinstance(ip_addresses, list):
            return 'iaas_vm_update_111'

        if len(ip_addresses) == 0:
            return 'iaas_vm_update_112'

        gateway_subnet = None
        if self._instance.gateway_subnet_id is not None:
            gateway_subnet = netaddr.IPNetwork(self._instance.gateway_subnet.address_range)

        ips = IPAddress.objects.filter(vm=self._instance.pk)

        # If any errors have occurred we are not going to update nats for ips
        if len(self._errors) > 0:
            return None

        # get the virtual_router associated with this vms project
        virtual_router = VirtualRouter.objects.get(project_id=self._instance.project.pk)
        region_subnet = virtual_router.ip_address.subnet

        nat_quantity = 0

        # get current nat quantity to modify for history nat_quantity
        for ip in ips:
            if ip.public_ip is not None:
                nat_quantity += 1

        current_nat_quantity = nat_quantity
        to_delete: Deque[IPAddress] = deque()
        to_rollback: Deque[IPAddress] = deque()
        for a in ip_addresses:
            nat = a.pop('nat', False)
            valid = False
            for ip in ips:
                if a['address'] == ip.address:
                    valid = True
                    if nat and ip.public_ip is None:
                        if gateway_subnet is None or \
                                a['address'] not in gateway_subnet:
                            return 'iaas_vm_update_113'
                        # Update IP to be NATed and create Floating IP
                        try:
                            public_ip = helpers.create_public_ip(
                                self.request,
                                region_subnet,
                                'iaas_vm_update_114',
                                self.span,
                            )
                            to_delete.append(public_ip)
                            ip.public_ip = public_ip
                            ip.save()
                        except helpers.IAASException as e:  # pragma: no cover
                            for ip in to_rollback:
                                ip.save()
                            for ip in to_delete:
                                ip.delete()
                            return e.args[0]

                        nat_quantity += 1
                        self.update_virtual_router = True

                    elif not nat and ip.public_ip is not None:
                        # Update IP to remove NAT
                        to_rollback.appendleft(ip.public_ip)
                        to_rollback.appendleft(ip)

                        ip.public_ip.deleted = datetime.utcnow()
                        ip.public_ip.save()

                        ip.public_ip = None
                        ip.save()
                        self.update_virtual_router = True
                        nat_quantity -= 1

                    break
            if not valid:
                return 'iaas_vm_update_115'

        if nat_quantity != current_nat_quantity:
            self._create_history()

            self.vm_history['nat_quantity'] = nat_quantity
            self.vm_history['nat_sku'] = skus.NAT_001

        return None

    def validate_cpu(self, cpu: Optional[int]) -> Optional[str]:
        """
        description: |
            The number of Virtual CPUs (vCPUs) that the VM should have after update.
        type: integer
        minimum: 1
        maximum: 24
        """
        if cpu is None or cpu == self._instance.cpu:
            return None

        try:
            cpu = int(cpu)
        except (ValueError, TypeError):
            return 'iaas_vm_update_116'

        if cpu <= 0:
            return 'iaas_vm_update_117'

        # If we are not updating the state in the request, the current VM state should be quiesced
        # And then we update it to be quiesced update
        if 'state' not in self.cleaned_data:
            self._create_history()

            if self._instance.state == states.RUNNING:
                self.cleaned_data['state'] = states.RUNNING_UPDATE
                self.vm_history['state'] = states.RUNNING_UPDATE
            elif self._instance.state == states.QUIESCED:
                self.cleaned_data['state'] = states.QUIESCED_UPDATE
                self.vm_history['state'] = states.QUIESCED_UPDATE
            else:
                return 'iaas_vm_update_118'

        else:
            # Check that the requested state change will be running / quiesced update states
            if self.cleaned_data['state'] not in UPDATE_STATES:
                return 'iaas_vm_update_119'

        # Lastly, check that the VM's server has the space for the cpu update
        if cpu > self._instance.cpu:
            diff = cpu - self._instance.cpu
            srv = self._instance.server
            if diff > (srv.vcpus_for_update - srv.vcpus_in_use):
                return 'iaas_vm_update_120'

        self.vm_history['cpu_quantity'] = cpu
        self.vm_history['cpu_sku'] = skus.VCPU_001

        self.cleaned_data['cpu'] = cpu

        return None

    def validate_ram(self, ram: Optional[int]) -> Optional[str]:
        """
        description: |
            The amount of RAM (in GB) that the VM should have.
        type: integer
        minimum: 1
        maximum: 128
        """
        if ram is None or ram == self._instance.ram:
            return None

        try:
            ram = int(ram)
        except (ValueError, TypeError):
            return 'iaas_vm_update_121'

        if ram <= 0:
            return 'iaas_vm_update_122'

        # If we are not updating the state in the request, the current VM state should be quiesced
        # And then we update it to be quiesced update
        if 'state' not in self.cleaned_data:
            self._create_history()
            if self._instance.state == states.RUNNING:
                self.cleaned_data['state'] = states.RUNNING_UPDATE
                self.vm_history['state'] = states.RUNNING_UPDATE
            elif self._instance.state == states.QUIESCED:
                self.cleaned_data['state'] = states.QUIESCED_UPDATE
                self.vm_history['state'] = states.QUIESCED_UPDATE
            else:
                return 'iaas_vm_update_123'

        else:
            # Check that the requested state change will be running / quiesced update states
            if self.cleaned_data['state'] not in UPDATE_STATES:
                return 'iaas_vm_update_124'

        # Lastly, check that the VM's server has the space for the ram update
        if ram > self._instance.ram:
            diff = ram - self._instance.ram
            srv = self._instance.server
            if diff > (srv.ram_for_update - srv.ram_in_use):
                return 'iaas_vm_update_125'

        self.vm_history['ram_quantity'] = ram
        self.vm_history['ram_sku'] = skus.RAM_001

        self.cleaned_data['ram'] = ram

        return None

    def validate_storages(self, storages: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """
        description: |
            An array of StorageCreate objects to create or update Storage objects for the VM.

            To update an existing Storage object, include the id field as well in the object.
        type: array
        items:
            $ref: '#/components/schemas/StorageCreate'
        """
        storages = storages or []
        if not isinstance(storages, list):
            return 'iaas_vm_update_126'

        if len(storages) == 0:
            return None

        # Create each of the storage instances for the sent details
        errors: List[Optional[Dict[str, Any]]] = [None for _ in range(len(storages))]
        instances: Deque[Storage] = deque()
        tracer = settings.TRACER
        size_increase = 0

        storages_to_update: List[int] = []

        for index, storage in enumerate(storages):
            if not isinstance(storage, dict):
                details = get_error_details('iaas_vm_update_127')
                errors[index] = details['iaas_vm_update_127']
                continue

            # Determine whether we are creating or updating
            storage_id = storage.get('id', None)
            if storage_id is None:
                with tracer.start_span(f'_create_storage_{index}', child_of=self.span) as span:
                    controller = StorageCreateController(data=storage, request=self.request, span=span)
                    # Validate the controller
                    if not controller.is_valid():
                        # If the controller isn't valid, add the errors to the list
                        errors[index] = controller.errors
                        continue
                    size_increase += controller.instance.gb
                    if controller.cleaned_data.get('primary', False):
                        details = get_error_details('iaas_vm_update_128')
                        errors[index] = details['iaas_vm_update_128']
                        continue
            else:
                with tracer.start_span(f'_update_storage_{index}', child_of=self.span) as span:
                    # Get the object
                    with tracer.start_span('fetch_object', child_of=span):
                        try:
                            obj = Storage.objects.get(pk=storage_id)
                        except Storage.DoesNotExist:
                            details = get_error_details('iaas_vm_update_129')
                            errors[index] = details['iaas_vm_update_129']
                            continue

                    controller = StorageUpdateController(instance=obj, data=storage, request=self.request, span=span)

                    # Validate the controller
                    if not controller.is_valid():
                        # If the controller isn't valid, add the errors to the list
                        errors[index] = controller.errors
                        continue
                    size_increase += controller.capacity_change

            if controller.cleaned_data.pop('update_history', False):
                storages_to_update.append(controller.instance.pk)

            # Add the instance to the instances deque
            instances.append(controller.instance)

        # Lastly, check that the VM's server has the space for the gb update and the VMs state was requested to update
        if size_increase > 0:
            srv = self._instance.server
            if size_increase > (srv.gb_for_update - srv.gb_in_use):
                return 'iaas_vm_update_130'
            # If we are not updating the state in the request, running or quiesced the current VM state should be to
            # be able to modify storages
            if 'state' not in self.cleaned_data:
                self._create_history()
                if self._instance.state == states.RUNNING:
                    self.cleaned_data['state'] = states.RUNNING_UPDATE
                    self.vm_history['state'] = states.RUNNING_UPDATE
                elif self._instance.state == states.QUIESCED:
                    self.cleaned_data['state'] = states.QUIESCED_UPDATE
                    self.vm_history['state'] = states.QUIESCED_UPDATE
                else:
                    return 'iaas_vm_update_131'
            else:
                # Check that the requested state change will be running / quiesced update states
                if self.cleaned_data['state'] not in UPDATE_STATES:
                    return 'iaas_vm_update_132'

        # Check if any storage item had an error, if so we want to store the errors
        if any(item is not None for item in errors):
            self._errors['storages'] = errors
            return None

        # If we make it here, then everything is fine
        self.cleaned_data['storages'] = instances
        self.cleaned_data['storages_to_update'] = storages_to_update

        return None

    def validate_userdata(self, userdata: Optional[str]) -> Optional[str]:
        """
        description: |
            Cloud Init allows Mime Multi-part messages, or files that start with a given set of strings
        type: str
        """
        if userdata is None:
            return None

        # Check if the OS image supports Cloud Init
        image = self._instance.image
        if not image.cloud_init:
            return 'iaas_vm_update_133'

        userdata = str(userdata).strip()
        if len(userdata) > self.get_field('userdata').max_length:
            return 'iaas_vm_update_134'

        valid = False
        for header in CLOUD_INIT_HEADERS:
            if userdata.startswith(header):
                valid = True
                break

        if not valid:
            # Check if it's a Mime Multi-part file
            if '\nMIME-Version: ' not in userdata:
                return 'iaas_vm_update_135'

        self.cleaned_data['userdata'] = userdata
        return None

    def validate_gpu(self, gpu: Optional[int]) -> Optional[str]:
        """
        description: |
            The number of GPUs to have attached to the VM
        type: integer
        """
        if gpu is None or gpu == self._instance.gpu:
            return None

        try:
            gpu = int(gpu)
        except (ValueError, TypeError):
            return 'iaas_vm_update_136'

        if len(Device.objects.filter(server=self._instance.server, device_type__sku__icontains='GPU')) == 0:
            return 'iaas_vm_update_137'

        if 'state' not in self.cleaned_data:
            self._create_history()
            if self._instance.state == states.RUNNING:
                self.cleaned_data['state'] = states.RUNNING_UPDATE
                self.vm_history['state'] = states.RUNNING_UPDATE
            elif self._instance.state == states.QUIESCED:
                self.cleaned_data['state'] = states.QUIESCED_UPDATE
                self.vm_history['state'] = states.QUIESCED_UPDATE
            else:
                return 'iaas_vm_update_138'
        else:
            if self.cleaned_data['state'] not in UPDATE_STATES:
                return 'iaas_vm_update_139'

        if gpu > self._instance.gpu:
            # Attach GPUs to VM, check server has capacity
            available_devices = Device.objects.filter(vm_id__isnull=True, server=self._instance.server)
            gpu_increase = gpu - self._instance.gpu
            if gpu_increase > len(available_devices):
                return 'iaas_vm_update_140'
            # If any errors have occurred we are not going to assign vm to devices. This is the reason for it being
            # validated last
            if len(self._errors) > 0:
                return None
            assigned = 0
            while assigned < gpu_increase:
                available_devices[assigned].vm_id = self._instance.pk
                available_devices[assigned].save()
                assigned += 1

        gpu_sku = Device.objects.filter(
            server=self._instance.server,
            device_type__sku__icontains='GPU',
        )[0].device_type.sku

        self.vm_history['gpu_quantity'] = gpu
        self.vm_history['gpu_sku'] = gpu_sku

        self.cleaned_data['gpu'] = gpu

        return None

    def _create_history(self):
        if not self.create_vm_history:
            self.create_vm_history = True
            self.vm_history = {}

        return None
