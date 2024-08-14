from .allocation import AllocationCreateController, AllocationUpdateController, AllocationListController
from .app_settings import AppSettingsCreateController, AppSettingsUpdateController
from .asn import ASNCreateController, ASNUpdateController, ASNListController
from .backup import BackupCreateController, BackupUpdateController, BackupListController
from .backup_history import BackupHistoryListController
from .ceph import CephCreateController, CephListController, CephUpdateController
from .cix_blacklist import CIXBlacklistCreateController, CIXBlacklistListController, CIXBlacklistUpdateController
from .cix_whitelist import CIXWhitelistListController, CIXWhitelistUpdateController, CIXWhitelistCreateController
from .cloud import CloudCreateController, CloudUpdateController
from .cloud_bill import CloudBillListController
from .device import DeviceCreateController, DeviceListController, DeviceUpdateController
from .device_type import DeviceTypeListController
from .domain import DomainCreateController, DomainListController
from .dynamic_remote_subnet import DynamicRemoteSubnetController
from .firewall_rule import FirewallRuleCreateController
from .image import ImageListController, ImageUpdateController
from .interface import InterfaceCreateController, InterfaceListController, InterfaceUpdateController
from .ip_address import IPAddressListController, IPAddressCreateController, IPAddressUpdateController
from .ipmi import IPMICreateController, IPMIListController
from .ip_validator import IPValidatorController
from .metrics import MetricsController
from .pool_ip import PoolIPListController, PoolIPUpdateController, PoolIPCreateController
from .project import ProjectListController, ProjectCreateController, ProjectUpdateController
from .ptr_record import PTRRecordCreateController, PTRRecordListController, PTRRecordUpdateController
from .record import RecordCreateController, RecordListController, RecordUpdateController
from .region_image import RegionImageCreateController
from .region_storage_type import RegionStorageTypeCreateController
from .route import RouteCreateController, RouteUpdateController
from .router import RouterListController, RouterCreateController, RouterUpdateController
from .run_robot import RunRobotTurnOffController
from .server import ServerListController, ServerCreateController, ServerUpdateController
from .server_type import ServerTypeListController
from .snapshot import SnapshotCreateController, SnapshotListController, SnapshotUpdateController
from .snapshot_history import SnapshotHistoryListController
from .storage import StorageCreateController, StorageListController
from .storage_type import StorageTypeListController, StorageTypeUpdateController
from .subnet import SubnetListController, SubnetUpdateController, SubnetCreateController, SubnetSpaceListController
from .virtual_router import VirtualRouterCreateController, VirtualRouterListController, VirtualRouterUpdateController
from .vm import VMListController, VMCreateController, VMUpdateController
from .vm_history import VMHistoryListController
from .vpn import VPNCreateController, VPNListController, VPNUpdateController
from .vpn_client import VPNClientCreateController, VPNClientUpdateController
from .vpn_history import VPNHistoryListController


__all__ = [
    # Allocation
    'AllocationCreateController',
    'AllocationListController',
    'AllocationUpdateController',

    # App Settings
    'AppSettingsCreateController',
    'AppSettingsUpdateController',

    # ASN
    'ASNCreateController',
    'ASNListController',
    'ASNUpdateController',

    # Backup
    'BackupCreateController',
    'BackupListController',
    'BackupUpdateController',

    # Backup History
    'BackupHistoryListController',

    # Blacklist
    'CIXBlacklistCreateController',
    'CIXBlacklistListController',
    'CIXBlacklistUpdateController',

    # Ceph
    'CephCreateController',
    'CephListController',
    'CephUpdateController',

    # Cloud
    'CloudCreateController',
    'CloudUpdateController',

    # Cloud Bill
    'CloudBillListController',

    # Device
    'DeviceCreateController',
    'DeviceListController',
    'DeviceUpdateController',

    # Device Type
    'DeviceTypeListController',

    # Domain
    'DomainCreateController',
    'DomainListController',

    # Dynamic Remote Subnet
    'DynamicRemoteSubnetController',

    # Whitelist
    'CIXWhitelistListController',
    'CIXWhitelistUpdateController',
    'CIXWhitelistCreateController',

    # Firewall Rule
    'FirewallRuleCreateController',

    # Image
    'ImageListController',
    'ImageUpdateController',

    # Interface
    'InterfaceCreateController',
    'InterfaceListController',
    'InterfaceUpdateController',

    # IPAddress
    'IPAddressListController',
    'IPAddressCreateController',
    'IPAddressUpdateController',

    # IPMI
    'IPMICreateController',
    'IPMIListController',

    # IP Validator
    'IPValidatorController',

    # Metrics
    'MetricsController',

    # Pool IP
    'PoolIPListController',
    'PoolIPUpdateController',
    'PoolIPCreateController',

    # Project
    'ProjectListController',
    'ProjectCreateController',
    'ProjectUpdateController',

    # PTR Record
    'PTRRecordListController',
    'PTRRecordUpdateController',
    'PTRRecordCreateController',

    # Record
    'RecordListController',
    'RecordUpdateController',
    'RecordCreateController',

    # RegionImage
    'RegionImageCreateController',

    # RegionStorageType
    'RegionStorageTypeCreateController',

    # Route
    'RouteCreateController',
    'RouteUpdateController',

    # Router
    'RouterListController',
    'RouterCreateController',
    'RouterUpdateController',

    # Run Robot
    'RunRobotTurnOffController',

    # Server
    'ServerListController',
    'ServerCreateController',
    'ServerUpdateController',

    # ServerType
    'ServerTypeListController',

    # Snapshot
    'SnapshotCreateController',
    'SnapshotListController',
    'SnapshotUpdateController',

    # Snapshot History
    'SnapshotHistoryListController',

    # Storage
    'StorageCreateController',
    'StorageListController',

    # StorageType
    'StorageTypeListController',
    'StorageTypeUpdateController',

    # Subnet
    'SubnetListController',
    'SubnetUpdateController',
    'SubnetCreateController',

    # Subnet Space
    'SubnetSpaceListController',


    # VirtualRouter
    'VirtualRouterCreateController',
    'VirtualRouterListController',
    'VirtualRouterUpdateController',

    # VM
    'VMListController',
    'VMCreateController',
    'VMUpdateController',

    # VMHistory
    'VMHistoryListController',

    # VPN
    'VPNCreateController',
    'VPNListController',
    'VPNUpdateController',

    # VPN
    'VPNClientCreateController',
    'VPNClientUpdateController',

    # VPNHistory
    'VPNHistoryListController',
]
