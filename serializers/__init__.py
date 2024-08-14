from .allocation import AllocationSerializer
from .app_settings import AppSettingsSerializer
from .asn import ASNSerializer
from .backup import BackupSerializer
from .backup_history import BackupHistorySerializer
from .bom import BOMSerializer
from .capacity import CapacitySerializer
from .cix_blacklist import CIXBlacklistSerializer
from .cix_whitelist import CIXWhitelistSerializer
from .cloud import CloudSerializer
from .device import DeviceSerializer
from .device_type import DeviceTypeSerializer
from .domain import DomainSerializer
from .firewall_rule import FirewallRuleSerializer
from .image import ImageSerializer
from .interface import InterfaceSerializer
from .ip_address import NATIPAddressSerializer, IPAddressSerializer
from .ipmi import IPMISerializer
from .ip_validator import IPValidatorSerializer
from .metrics import MetricsSerializer  # noqa: F401
from .policy_log import PolicyLogSerializer  # noqa: F401
from .pool_ip import PoolIPSerializer
from .project import ProjectSerializer
from .record import RecordSerializer
from .region_image import RegionImageSerializer  # pragma: no cover
from .region_storage_type import RegionStorageTypeSerializer  # pragma: no cover
from .resource import ResourceSerializer
from .route import RouteSerializer
from .router import RouterSerializer
from .router_metrics import RouterMetricsSerializer
from .server import ServerSerializer
from .server_metrics import ServerMetricsSerializer
from .server_type import ServerTypeSerializer
from .snapshot import SnapshotSerializer, SnapshotTreeSerializer
from .snapshot_history import SnapshotHistorySerializer
from .storage import StorageSerializer
from .storage_history import StorageHistorySerializer
from .storage_type import StorageTypeSerializer
from .subnet import (
    RelatedSubnetSerializer,
    SubnetSerializer,
    SubnetSpaceSerializer,
)
from .virtual_router import BaseVirtualRouterSerializer, VirtualRouterSerializer
from .vm import BaseVMSerializer, VMSerializer
from .vm_history import VMHistorySerializer
from .vpn import BaseVPNSerializer, VPNSerializer
from .vpn_history import VPNHistorySerializer
from .vpn_client import VPNClientSerializer
from .vpn_status import VPNStatusSerializer


__all__ = [
    # Allocation
    'AllocationSerializer',

    # App Settings
    'AppSettingsSerializer',

    # ASN
    'ASNSerializer',

    # Backup
    'BackupSerializer',

    # Backup History
    'BackupHistorySerializer',

    # BOM
    'BOMSerializer',

    # Capacity
    'CapacitySerializer',

    # Blacklist
    'CIXBlacklistSerializer',

    # Whitelist
    'CIXWhitelistSerializer',

    # Cloud
    'CloudSerializer',

    # Device
    'DeviceSerializer',

    # Device Type
    'DeviceTypeSerializer',

    # Domain
    'DomainSerializer',

    # FirewallRule
    'FirewallRuleSerializer',

    # Image
    'ImageSerializer',

    # Interface
    'InterfaceSerializer',

    # IPAddress
    'NATIPAddressSerializer',
    'IPAddressSerializer',

    # IP Validator
    'IPValidatorSerializer',

    # IPMI
    'IPMISerializer',

    # Metrics
    'MetricsSerializer',  # just for docs

    # Policy Log
    'PolicyLogSerializer',

    # Pool IP
    'PoolIPSerializer',

    # Project
    'ProjectSerializer',

    # Record
    'RecordSerializer',

    # RegionImage,
    'RegionImageSerializer',

    # RegionStorageType
    'RegionStorageTypeSerializer',

    # Resource
    'ResourceSerializer',

    # Route
    'RouteSerializer',

    # Router
    'RouterSerializer',

    # RouterMetrics
    'RouterMetricsSerializer',

    # Server
    'ServerSerializer',

    # ServerMetrics
    'ServerMetricsSerializer',

    # ServerType
    'ServerTypeSerializer',

    # Snapshot
    'SnapshotSerializer',
    'SnapshotTreeSerializer',

    # Snapshot History
    'SnapshotHistorySerializer',

    # storage
    'StorageSerializer',

    # Storage History
    'StorageHistorySerializer',

    # Storage Type
    'StorageTypeSerializer',

    # Subnet
    'RelatedSubnetSerializer',
    'SubnetSerializer',
    'SubnetSpaceSerializer',

    # Virtual Router
    'BaseVirtualRouterSerializer',
    'VirtualRouterSerializer',

    # VM
    'BaseVMSerializer',
    'VMSerializer',

    # VMHistory
    'VMHistorySerializer',

    # VPN
    'BaseVPNSerializer',
    'VPNSerializer',

    # VPN Client
    'VPNClientSerializer',

    # VPN History
    'VPNHistorySerializer',

    # VPN Status
    'VPNStatusSerializer',
]
