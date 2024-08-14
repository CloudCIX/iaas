# python
from typing import Optional
# libs
# from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from iaas.models import (
    IPAddress,
    Subnet,
    VirtualRouter,
)

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request, subnet: Subnet) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - The User's Address owns the IPAddress' subnet.
        """
        if request.user.address['id'] not in {subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: IPAddress) -> Optional[Http403]:
        """
        The request to read a IPAddress record is valid if:
        - The User's Address owns the IPAddress' Subnet
        - IP Address is from a Project subnet, robot for region of project can read
        - IP Address is for public IP of VM in users project
        - IP Address for virtual router in users project
        """
        # The User's Address owns the IPAddress' Subnet
        if request.user.address['id'] in {obj.subnet.address_id, 1}:
            return None

        # Robot Permission
        if request.user.robot:
            # Robot can read Project Network IPs in its region
            if not obj.subnet.from_project_network:
                return Http403(error_code='iaas_ip_address_read_201')
            if request.user.address['id'] != obj.vm.project.region_id:
                return Http403(error_code='iaas_ip_address_read_202')

        else:
            user_address = request.user.address['id']
            # IP Address is for Public IP of VM in users project
            private_ip = IPAddress.objects.filter(public_ip=obj.id).first()
            if private_ip is not None and private_ip.vm.project.address_id != user_address:
                return Http403(error_code='iaas_ip_address_read_203')

            # IP Address is for Virtual Router in users project
            router_ip = VirtualRouter.objects.filter(ip_address=obj).first()
            if router_ip is not None and router_ip.project.address_id != user_address:
                return Http403(error_code='iaas_ip_address_read_204')

            if private_ip is None and router_ip is None:
                # IP not connected to a project, therefore user cannot read.
                return Http403(error_code='iaas_ip_address_read_205')

        return None

    @staticmethod
    def update(request: Request, obj: IPAddress) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - IP Address is not from a Project RFC1918 subnet
        - The User's Address owns the IPAddress' Subnet
        - It is not related to a VM or Virtual Router IP Address
        """
        # Only robot users can update via the cloud resource RFC1918 IPs
        if obj.subnet.from_project_network:
            return Http403(error_code='iaas_ip_address_update_201')

        # The User's Address owns the IPAddress' Subnet
        if request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_update_202')

        # It is not a connected to a VM or Virtual Router IP Address
        private_ip = IPAddress.objects.filter(public_ip=obj.id)
        virtual_router = VirtualRouter.objects.filter(ip_address=obj)
        if len(private_ip) > 0 or len(virtual_router) > 0:
            return Http403(error_code='iaas_ip_address_update_203')

        return None

    @staticmethod
    def delete(request: Request, obj: IPAddress) -> Optional[Http403]:
        """
        The request to create a IPAddress record is valid if:
        - It is not a RFC1918 IP for a Project
        - The User's Address owns the IPAddress' Subnet
        - It is not connected to a VM or Virtual Router IP Address
        """
        # Only robot users can delete via the cloud resource RFC1918 IPs
        if obj.subnet.from_project_network:
            return Http403(error_code='iaas_ip_address_delete_201')

        # The User's Address owns the IPAddress' Subnet
        if request.user.address['id'] not in {obj.subnet.address_id, 1}:
            return Http403(error_code='iaas_ip_address_delete_202')

        # It is not a connected to a VM or Virtual Router IP Address
        private_ip = IPAddress.objects.filter(public_ip=obj.id)
        virtual_router = VirtualRouter.objects.filter(ip_address=obj)
        if len(private_ip) > 0 or len(virtual_router) > 0:
            return Http403(error_code='iaas_ip_address_delete_203')

        return None
