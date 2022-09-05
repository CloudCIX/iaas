# stdlib
from typing import List
# lib
from django.urls import path, register_converter
# local
from . import views, converters

register_converter(converters.CIDRConverter, 'cidr')


urlpatterns: List[path] = [
    # Allocation
    path(
        'allocation/',
        views.AllocationCollection.as_view(),
        name='allocation_collection',
    ),

    path(
        'allocation/<int:pk>/',
        views.AllocationResource.as_view(),
        name='allocation_resource',
    ),

    # App Settings
    path(
        'app_settings/',
        views.AppSettingsCollection.as_view(),
        name='app_settings_collection',
    ),

    path(
        'app_settings/<int:pk>/',
        views.AppSettingsResource.as_view(),
        name='app_settings_resource',
    ),

    # ASN
    path(
        'asn/',
        views.ASNCollection.as_view(),
        name='asn_collection',
    ),

    path(
        'asn/<int:pk>/',
        views.ASNResource.as_view(),
        name='asn_resource',
    ),

    # Backup
    path(
        'backup/',
        views.BackupCollection.as_view(),
        name='backup_collection',
    ),
    path(
        'backup/<int:pk>/',
        views.BackupResource.as_view(),
        name='backup_resource',
    ),

    # Backup History
    path(
        'backup_history/',
        views.BackupHistoryCollection.as_view(),
        name='backup_history_collection',
    ),

    # Blacklist
    path(
        'cix_blacklist/',
        views.CIXBlacklistCollection.as_view(),
        name='cix_blacklist_collection',
    ),

    path(
        'cix_blacklist/<cidr:cidr>/',
        views.CIXBlacklistResource.as_view(),
        name='cix_blacklist_resource',
    ),

    # Whitelist
    path(
        'cix_whitelist/',
        views.CIXWhitelistCollection.as_view(),
        name='cix_whitelist_collection',
    ),

    path(
        'cix_whitelist/<cidr:cidr>/',
        views.CIXWhitelistResource.as_view(),
        name='cix_whitelist_resource',
    ),

    # Cloud
    path(
        'cloud/',
        views.CloudCollection.as_view(),
        name='cloud_collection',
    ),
    path(
        'cloud/<int:pk>/',
        views.CloudResource.as_view(),
        name='cloud_resource',
    ),

    # CloudBill
    path(
        'cloud/pricing/',
        views.CloudBillCollection.as_view(),
        name='cloud_bill_collection',
    ),
    path(
        'cloud/pricing/<int:project_id>/',
        views.CloudBillResource.as_view(),
        name='cloud_bill_resource',
    ),


    # Domain
    path(
        'domain/',
        views.DomainCollection.as_view(),
        name='domain_collection',
    ),

    path(
        'domain/<int:pk>/',
        views.DomainResource.as_view(),
        name='domain_resource',
    ),

    # Dynamic Subnet
    path(
        'dynamic_remote_subnet/<int:region_id>/',
        views.DynamicRemoteSubnetResource.as_view(),
        name='dynamic_remote_subnet_resource',
    ),

    # Image
    path(
        'image/',
        views.ImageCollection.as_view(),
        name='image_collection',
    ),
    path(
        'image/<int:pk>/',
        views.ImageResource.as_view(),
        name='image_resource',
    ),

    # Interface
    path(
        'interface/',
        views.InterfaceCollection.as_view(),
        name='interface_collection',
    ),
    path(
        'interface/<int:pk>/',
        views.InterfaceResource.as_view(),
        name='interface_resource',
    ),

    # IPAddress
    path(
        'ip_address/',
        views.IPAddressCollection.as_view(),
        name='ip_address_collection',
    ),

    path(
        'ip_address/<int:pk>/',
        views.IPAddressResource.as_view(),
        name='ip_address_resource',
    ),

    # IPMI
    path(
        'ipmi/',
        views.IPMICollection.as_view(),
        name='ipmi_collection',
    ),

    path(
        'ipmi/<int:pk>/',
        views.IPMIResource.as_view(),
        name='ipmi_resource',
    ),

    # IPValidator
    path(
        'ip_validator/',
        views.IPValidator.as_view(),
        name='ip_validator',
    ),

    # Metrics
    path(
        'metrics/<int:region_id>/',
        views.MetricsResource.as_view(),
        name='metrics_resource',
    ),

    # PolicyLog
    path(
        'policy_log/<int:project_id>/',
        views.PolicyLogCollection.as_view(),
        name='policy_log_collection',
    ),

    # Pool IP
    path(
        'pool_ip/',
        views.PoolIPCollection.as_view(),
        name='pool_ip_collection',
    ),

    path(
        'pool_ip/<int:pk>/',
        views.PoolIPResource.as_view(),
        name='pool_ip_resource',
    ),

    # Project
    path(
        'project/',
        views.ProjectCollection.as_view(),
        name='project_collection',
    ),
    path(
        'project/<int:pk>/',
        views.ProjectResource.as_view(),
        name='project_resource',
    ),

    # PTR Record
    path(
        'ptr_record/',
        views.PTRRecordCollection.as_view(),
        name='ptr_record_collection',
    ),

    path(
        'ptr_record/<int:pk>/',
        views.PTRRecordResource.as_view(),
        name='ptr_record_resource',
    ),

    # Record
    path(
        'record/',
        views.RecordCollection.as_view(),
        name='record_collection',
    ),

    path(
        'record/<int:pk>/',
        views.RecordResource.as_view(),
        name='record_resource',
    ),

    # RegionImage
    path(
        'region_image/',
        views.RegionImageCollection.as_view(),
        name='region_image_collection',
    ),

    path(
        'region_image/<int:image_id>/',
        views.RegionImageResource.as_view(),
        name='region_image_resource',
    ),

    # Router
    path(
        'router/',
        views.RouterCollection.as_view(),
        name='router_collection',
    ),
    path(
        'router/<int:pk>/',
        views.RouterResource.as_view(),
        name='router_resource',
    ),

    # RunRobot
    path(
        'run_robot/',
        views.RunRobotCollection.as_view(),
        name='run_robot_collection',
    ),

    # Server
    path(
        'server/',
        views.ServerCollection.as_view(),
        name='server_collection',
    ),
    path(
        'server/<int:pk>/',
        views.ServerResource.as_view(),
        name='server_resource',
    ),

    # ServerType
    path(
        'server_type/',
        views.ServerTypeCollection.as_view(),
        name='server_type_collection',
    ),
    path(
        'server_type/<int:pk>/',
        views.ServerTypeResource.as_view(),
        name='server_type_resource',
    ),

    # Snapshot
    path(
        'snapshot/',
        views.SnapshotCollection.as_view(),
        name='snapshot_collection',
    ),
    path(
        'snapshot/<int:pk>/',
        views.SnapshotResource.as_view(),
        name='snapshot_resource',
    ),
    path(
        'snapshot_tree/<int:vm_id>/',
        views.SnapshotTreeResource.as_view(),
        name='snapshot_tree_resource',
    ),
    # Snapshot History
    path(
        'snapshot_history/',
        views.SnapshotHistoryCollection.as_view(),
        name='snapshot_history_collection',
    ),

    # Storage
    path(
        'vm/<int:vm_id>/storage/',
        views.StorageCollection.as_view(),
        name='storage_collection',
    ),
    path(
        'vm/<int:vm_id>/storage/<int:pk>/',
        views.StorageResource.as_view(),
        name='storage_resource',
    ),

    # StorageType
    path(
        'storage_type/',
        views.StorageTypeCollection.as_view(),
        name='storage_type_collection',
    ),
    path(
        'storage_type/<int:pk>/',
        views.StorageTypeResource.as_view(),
        name='storage_type_resource',
    ),

    # Subnet
    path(
        'subnet/',
        views.SubnetCollection.as_view(),
        name='subnet_collection',
    ),

    path(
        'subnet/<int:pk>/',
        views.SubnetResource.as_view(),
        name='subnet_resource',
    ),

    # Subnet Space
    path(
        'subnet_space/<int:allocation_id>/',
        views.SubnetSpaceCollection.as_view(),
        name='subnet_space_collection',
    ),

    # VirtualRouter
    path(
        'virtual_router/',
        views.VirtualRouterCollection.as_view(),
        name='virtual_router_collection',
    ),
    path(
        'virtual_router/<int:pk>/',
        views.VirtualRouterResource.as_view(),
        name='virtual_router_resource',
    ),

    # VM
    path(
        'vm/',
        views.VMCollection.as_view(),
        name='vm_collection',
    ),
    path(
        'vm/<int:pk>/',
        views.VMResource.as_view(),
        name='vm_resource',
    ),

    # VM History
    path(
        'vm_history/',
        views.VMHistoryCollection.as_view(),
        name='vm_history_collection',
    ),

    # VPN
    path(
        'vpn/',
        views.VPNCollection.as_view(),
        name='vpn_collection',
    ),
    path(
        'vpn/<int:pk>/',
        views.VPNResource.as_view(),
        name='vpn_resource',
    ),

    # VPN History
    path(
        'vpn_history/',
        views.VPNHistoryCollection.as_view(),
        name='vpn_history_collection',
    ),

    # VPN Status
    path(
        'vpn_status/<int:pk>/',
        views.VPNStatusResource.as_view(),
        name='vpn_status_resource',
    ),
]
