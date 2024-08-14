"""
Views for VM
"""
# stdlib
from typing import Any, Dict, List, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import skus, state
from iaas.models import (
    IPAddress,
    Server,
    StorageHistory,
    VM,
    VMHistory,
)
from iaas.permissions.vm import Permissions
from iaas.controllers import VMListController, VMCreateController, VMUpdateController
from iaas.serializers import BaseVMSerializer, VMSerializer
from iaas.utils import get_addresses_in_member, get_vm_interface_mac_address


__all__ = [
    'VMCollection',
    'VMResource',
]


class VMCollection(APIView):
    """
    Handles methods regarding VM that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List VM records

        description: |
            Retrieve a list of the Virtual Machines that the requesting User owns.

        responses:
            200:
                description: A list of VM records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VMListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all vms for addresses in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(project__address_id__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(project__address_id=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = VM.objects.filter(
                    **controller.cleaned_data['search'],
                )

                if address_filtering:
                    objs = objs.filter(address_filtering)

                objs = objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_vm_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'total_records': objs.count(),
                'warnings': controller.warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            include_related = request.GET.get('include_related', 'true').lower() in ['true']
            if include_related:
                data = VMSerializer(instance=objs, many=True).data
            else:
                data = BaseVMSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new VM

        description: Create a new VM with data given by user

        responses:
            201:
                description: VM record was created successfully
            400:
                description: Input data was invalid
                content:
                    application/json:
                        schema:
                            oneOf:
                                - $ref: '#/components/schemas/Error'
                                # Define the special version of multi error that may contain an array of errors
                                # for the storages key
                                - type: object
                                  description: |
                                    A map of field names to Error objects representing an error that was found with the
                                    data supplied for that field.

                                    In the case of the `storages` field, the returned data will be an array, with one of
                                    those objects in each position corresponding to each storage in the sent array that
                                    gave an error, or null if there wasn't an error with the corresponding storage.
                                  required:
                                    - errors
                                  properties:
                                    errors:
                                      type: object
                                      additionalProperties:
                                        oneOf:
                                          - $ref: '#/components/schemas/Error'
                                          - type: array
                                            items:
                                              $ref: '#/components/schemas/Error'
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VMCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            storages = controller.cleaned_data.pop('storages')
            ip_addresses = controller.cleaned_data.pop('ip_addresses', [])
            controller.instance.state = state.IN_API
            controller.instance.save()

        # Create IP Addresses for VM
        with tracer.start_span('saving_vm_ips', child_of=request.span):
            # Only one IP from each subnet(interface) on a VM needs to assigned a mac_address
            mac_address_subnets: List = []
            region_id = controller.instance.project.region_id
            server_type_id = controller.instance.server.type.id
            for ip in ip_addresses:
                ip_address = IPAddress.objects.create(
                    vm=controller.instance,
                    modified_by=self.request.user.id,
                    **ip,
                )
                if ip['subnet'].pk not in mac_address_subnets:
                    ip_address.mac_address = get_vm_interface_mac_address(region_id, server_type_id, ip_address.pk)
                    ip_address.save()
                    mac_address_subnets.append(ip['subnet'].pk)

        storage_history: List[Dict[str, Any]] = []
        with tracer.start_span('saving_storages', child_of=request.span):
            instances = []
            storage_type_sku = controller.vm_history.pop('storage_type_sku')
            for storage in storages:
                item: Dict[str, Any] = {}
                storage.vm = controller.instance
                storage.save()
                instances.append(storage)
                item = {
                    'gb_quantity': storage.gb,
                    'gb_sku': storage_type_sku,
                    'storage_name': storage.name,
                    'storage_id': storage.pk,
                }
                storage_history.append(item)

            controller.instance.storages.set(instances)

        with tracer.start_span('generate_vm_history', child_of=request.span):
            history = VMHistory.objects.create(
                modified_by=request.user.id,
                customer_address=request.user.address['id'],
                project_id=controller.instance.project.pk,
                project_vm_name=f'{controller.instance.project.name}_{controller.instance.name}',
                state=state.REQUESTED,
                vm=controller.instance,
                **controller.vm_history,
            )
        with tracer.start_span('generate_storage_history', child_of=request.span):
            for line in storage_history:
                StorageHistory.objects.create(
                    vm_history=history,
                    **line,
                )

        with tracer.start_span('update_vm_state', child_of=request.span):
            controller.instance.state = state.REQUESTED
            controller.instance.save()

        with tracer.start_span('setting_run_robot_flags', child_of=request.span):
            controller.instance.project.set_run_robot_flags()

        with tracer.start_span('set_storage_type', child_of=request.span):
            controller.instance.refresh_from_db()
            server = Server.objects.get(pk=controller.instance.server_id)
            storage_type = server.storage_type.name

        with tracer.start_span('serializing_data', child_of=request.span):
            controller.instance.storage_type = storage_type
            data = VMSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class VMResource(APIView):
    """
    Handles methods regarding VM that do require a specific id
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a VM record by the given `pk`.
        description: Verify if a VM record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the VM.
                type: integer

        responses:
            200:
                description: Requested VM exists and requesting User can access.
            404:
                description: Requesting user cannot access VM if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VM.objects.get(pk=pk)
            except VM.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a VM

        description: |
            Attempt to read information about a specific VM, returning 404 if VM doesn't exist or
            403 if user doesn't have permission.

        path_params:
            pk:
                description: The id of the VM to Read
                type: integer

        responses:
            200:
                description: Reads a VM
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VM.objects.get(pk=pk)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_vm_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('set_storage_type', child_of=request.span):
            server = Server.objects.get(pk=obj.server_id)
            obj.storage_type = server.storage_type.name

        with tracer.start_span('fetching_email_addresses', child_of=request.span) as child_span:
            modified_by = VMHistory.objects.filter(
                vm_id=obj.pk,
                state__in=state.SEND_EMAIL_STATES,
            ).order_by('-created')[0].modified_by
            manager_id = obj.project.manager_id
            params = {'id__in': [modified_by, manager_id]}
            users = Membership.user.list(
                token=request.auth,
                params=params,
                span=child_span,
            ).json()['content']
            emails = []
            for user in users:
                emails.append(user['email'])
            obj.emails = emails

        with tracer.start_span('serializing_data', child_of=request.span):
            data = VMSerializer(instance=obj).data
        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified VM

        description: |
            Attempt to update a VM by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the VM to be updated
                type: integer

        responses:
            200:
                description: VM was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VM.objects.get(pk=pk)
            except VM.DoesNotExist:
                return Http404(error_code='iaas_vm_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VMUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('generating_vm_history', child_of=request.span) as child_span:
            if controller.create_vm_history:
                history = VMHistory.objects.create(
                    modified_by=request.user.id,
                    customer_address=obj.project.address_id,
                    project_id=obj.project.pk,
                    project_vm_name=f'{obj.project.name}_{controller.instance.name}',
                    vm=controller.instance,
                    **controller.vm_history,
                )

                with tracer.start_span('saving_storages_and_history', child_of=child_span):
                    storages_to_update = controller.cleaned_data.pop('storages_to_update', [])
                    for storage in controller.cleaned_data.get('storages', []):
                        # If storage is new, save it now for an id to be created
                        create_storage_history = False
                        if storage.pk is None:
                            # Save it and append to the deque
                            storage.vm_id = obj.pk
                            storage.save()
                            create_storage_history = True
                        else:
                            if storage.pk in storages_to_update:
                                create_storage_history = True
                            storage.save()
                        if create_storage_history:
                            sku = skus.STORAGE_SKU_MAP[obj.server.storage_type_id]
                            StorageHistory.objects.create(
                                vm_history=history,
                                gb_quantity=storage.gb,
                                gb_sku=sku,
                                storage_name=storage.name,
                                storage_id=storage.pk,
                            )

        with tracer.start_span('closing_object', child_of=request.span):
            if controller.close_vm:
                obj.set_deleted()

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        # Update Virtual Router if we can and have to
        with tracer.start_span('update_virtual_router', child_of=request.span):
            virtual_router = obj.project.virtual_router
            if controller.update_virtual_router and virtual_router.can_update():
                if virtual_router.state == state.RUNNING:
                    virtual_router.state = state.RUNNING_UPDATE
                elif virtual_router.state == state.QUIESCED:
                    virtual_router.state = state.QUIESCED_UPDATE

                virtual_router.save()

        if not request.user.robot or controller.close_vm:
            with tracer.start_span('setting_run_robot_flags', child_of=request.span):
                obj.project.set_run_robot_flags()

        with tracer.start_span('set_storage_type', child_of=request.span):
            server = Server.objects.get(pk=obj.server_id)
            storage_type = server.storage_type.name

        with tracer.start_span('serializing_data', child_of=request.span):
            controller.instance.storage_type = storage_type
            data = VMSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a VM
        """
        return self.put(request, pk, True)
