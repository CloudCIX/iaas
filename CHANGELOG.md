# Changelog

## 3.3.2
Date: 2024-11-05

- Bug Fix:: If `vm.userdata` is an empty string and `image.cloudinit` is False, do not proceed in validation.


## 3.3.1
Date: 2024-10-07

- Bug Fix:: Extended `run_robot.list` service to include ``ceph`` dictionary in succesful responses.

## 3.3.0
Date: 2024-10-04

- Service: Added `ip_address_group.list` service.
- Enhancement: Added list seach filter to IP Address for `subnet__virtual_router_id` 
- Enhancement: Extended ``vm`` response to return `image_id`

## 3.2.1
Date: 2024-08-06

- Bug Fix: `robot` user can be a private user but they can still manage cloud infrastructure.

## 3.2.0
Date: 2024-08-01

- Extended cloud infrastructure permissions to not allow private users to manage cloud infrastructure.
- Add `mac_address` to IP Address model which is generated for VMs based on the server type ID, region ID and PK of the IP Address.

## 3.1.1
Date: 2024-07-09

- Improved Documentation
- Enhancement: Added list seach filter to Server for `interfaces__ip_address` 

## 3.1.0
Date: 2024-07-03

- Bug Fix: Updated Rage4 service to comply with the updated endpoints. 

## 3.0.0
Date: 2024-06-21

- CloudCIX Major release of Version 3. 
- CloudCIX Framework base incremented from Python 3.7 to Python 3.8

## 2.2.0
Date: 2024-03-21

- Enhancement: Extend GPUs supported to include H100 GPU.

## 2.1.1
Date: 2024-03-04

- Enhancement: Extended VM order by list to include `updated`.

## 2.1.0
Date: 2024-02-27

- Enhancement: Updated `netaddr` requests to changes in version [1.0.0](https://netaddr.readthedocs.io/en/latest/changes.html#release-1-0-0)

## 2.0.3
Date: 2024-02-20

- Bug Fix: ``ceph.update`` creating new BOM when size of CEPH resource is increased. 

## 2.0.2
Date: 2024-01-18

- Bug Fix: Calling the `set_run_robot_flag` function for a project.update request if it includes changing the state of all the cloud infrastructure in the Project. 

## 2.0.1
Date: 2024-01-05

- Bug Fix: Comparison logic in ``ceph.attach`` service.

## 2.0.0
Date: 2024-01-02

- CloudCIX Major release of Version 2

## 1.3.1
Date: 2023-12-18

- Bug Fix: Detach service 

## 1.3.0
Date: 2023-12-04

- Service: Removed ``vpns`` from Cloud service. They will be managed by only the VPN service only.
- Service: Added ``ceph.list``, ``ceph.read`` and ``ceph.update`` services. 
- Service: Added ``attach.update`` service to manage attaching one resource to another.
- Service: Added ``detach.update`` service to manage detaching one resource from another.
- Enhancement: Added `name` property to ``resource`` model.
- Enhancement: Remvoed `resource_type` model and replaced with a python file to store the constants.
- Enhancement: Extended ``run_robot.list`` response to return `ceph`

## 1.2.1
Date: 2023-11-16

- Enhancement: Extended upper RAM Create Limit for a VM to 88% of a servers RAM capacity

## 1.2.0
Date: 2023-09-05

- Documentation improvements

## 1.1.0
Date: 2023-07-18

- Service: Added ``ceph.create``
- Enhancement: In a region cache boolean to indicate if there are changes in the region and that the ``run_robot.list`` service should query the database for the list of changes to be processed by robot. 

## 1.0.18
Date: 2023-06-07

- Enhancement: Removed upper limit for `cpu` and `ram` in ``vm.create`` and ``vm.update`` services.

## 1.0.17
Date: 2023-05-15

- Enhancement: Removed `cloud` field from `ip_address` and `subnet`. This can determined if the ASN Number is greater than 1 trillion.
- Enhancement: Added support for search field `subnet__allocation__asn__number` on ``ip_address``
- Enhancement: Added support for search field `allocation__asn__number` on ``subnet``

## 1.0.16
Date: 2023-04-28

- Enhancement: Default ordering for list of storages will be by `primary` first and then `name`.

## 1.0.15
Date: 2023-04-26

- Bug Fix: Ensure a ``device`` is not attached to a ``vm`` for scrub requests.

## 1.0.14
Date: 2023-03-31

- Enhancement: Added suport for Image Windows Server 2022


## 1.0.13
Date: 2023-03-23

- Service: Added ``device_type.list`` service which returns a list of Device Types available in CloudCIX e.g. GPU devices
- Service: Added ``device`` service for the following methods: create, read, update and list. 
- Service: Extended ``snapshot.create`` and ``snapshot.update`` to not allow request if a device is attached to the VM. 

## 1.0.12
Date: 2023-02-04

- Enhancement: The following changes made in the ``vpn`` model to be compatible with [strongSwan](https://strongswan.org/) for PodNet:
    - Authentication Algorithms: Removed Support for `md5` and `hmac-md5-96`
    - Encryption Algorithms: Removed Support for `des-cbc` and `3des-cbc`
    - Removed `ike_mode`
    - Added `ike_local_identifier` and `ike_remote_identifier`
- Enhancement: Improved the `klinavicius` and `get_suitability` function in the ``server`` model which returns a value between 0 and |V|. These are used by the ``vm.create`` service to determine which ``server`` to place the ``vm`` on. 

## 1.0.11
Date: 2022-10-28

- Service: Added ``capacity.list`` returns the specs of the largest VMs a region can currently support. 

## 1.0.10
Date: 2022-09-29

- Bug Fix: Change in Rage4 service where Reverse Domains are created via the Domain create service. 

## 1.0.9
Date: 2022-09-22

- Enhancement: Extended ``project`` model with `grace_period` property.

## 1.0.8
Date: 2022-09-05

- Enhancement: Extended ``vm.update`` service to support updating `cpu`, `ram` and `storages[n].gb`. 

# 1.0.7
Date: 2022-04-29

- Enhancement: Improve log message for ``vm`` create controller if a server could not be found to place requested VM on.

# 1.0.6
Date: 2022-04-14

- Bug Fix: Change in Rage4 service where the default value for `priority` is `1` 
- Enhancement: Improved logging to responses from Rage4 services. 
- Enhancement: In ``ptr_record`` and ``record`` model renamed `time_to_live` to `ttl`


# 1.0.5
Date: 2022-04-01

- Enhancement: Added suport for Image Rocky Linux 8.4 and Rocky Linux 8.5


# 1.0.4
Date: 2022-03-27

- Enhancement: Extended ``backup`` model with `name` property.
- Enhancement: Extended ``vm`` model with `userdata` property.
- Enhancement: Added a default `ordering` property to all Model Meta classes. 

# 1.0.3
Date: 2022-02-02

- Service: Added ``cloudbill.list`` returns the SKU information for all the Projects the User has access to.

## 1.0.2
Date: 2022-01-12

- Enhancement: Extended VPN site-to-site tunnel to support FQDN or Public IP as the gateway on the remote side.
- Enhancement: Extended permission for ``backup``, ``cloud``, ``project``, ``snapshot``, ``storage``, ``virtual_router``, ``vm`` and ``vpn`` services for list, read and head requests to include Global Active users in the address's member.
- Bug Fix: ``snapshot.updata`` allow for the current snapshot to be reverted to.

## 1.0.1
Date: 2021-12-14

- Service: Added `snapshot_tree.read` for user to read the tree structure of Snapshots for the specified VM
- Enhancement: Extended ``interface.update`` service to allow for update of `hostname`, `ip_address` and `mac_address`.
- Bug Fix: ``vm.create`` validation of `gateway_subnet` is required, not optional. 
- Bug Fix: Miminum size of the Primary drive for a Windows OS is 32GB

## 1.0.0
Date: 2021-11-15

- Initial Docker release of CloudCIX IaaS Application 

## 0.0.0
Date: 2021-04-30

- Initial Python3 release of CloudCIX IaaS Application
