"""
Views for VPN
"""
# stdlib
from typing import List, Optional
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
from iaas import skus
from iaas import state as states
from iaas.controllers.helpers import get_stif_number, IAASException, get_ike_identifier
from iaas.models import VirtualRouter, VPN, VPNHistory
from iaas.permissions.vpn import Permissions
from iaas.controllers import VPNCreateController, VPNListController, VPNUpdateController
from iaas.serializers import BaseVPNSerializer, VPNSerializer
from iaas.utils import get_addresses_in_member


__all__ = [
    'VPNCollection',
    'VPNResource',
]


class VPNCollection(APIView):
    """
    Handles methods regarding VM that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List VPN records.

        description: |
            Retrieve a list of the VPN Tunnels that the requesting User owns.

        responses:
            200:
                description: A list of VPN records
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VPNListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(virtual_router__project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all vpn records for project's in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(
                        virtual_router__project__address_id__in=get_addresses_in_member(request, span),
                    )
                else:
                    address_filtering = Q(virtual_router__project__address_id=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = VPN.objects.filter(
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
                return Http400(error_code='iaas_vpn_list_001')

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
                data = VPNSerializer(instance=objs, many=True).data
            else:
                data = BaseVPNSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new VPN record in a specified Virtual Router.

        description: |
            Endpoint to create a new VPN Tunnel in a given Virtual Router.

            After creation, the Virtual Router will be set to the UPDATE state to build the new VPN Tunnel
            As a result, this method can only be fully executed if the chosen VirtualRouter is in a state that can be
            moved to the UPDATE state.

        responses:
            201:
                description: The newly created VPN record
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VPNCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        routes = controller.cleaned_data.pop('routes')
        if controller.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            vpn_clients = controller.cleaned_data.pop('vpn_clients')

        with tracer.start_span('checking_virtual_router', child_of=request.span):
            if not controller.instance.virtual_router.can_update():
                return Http400(error_code='iaas_vpn_create_001')

        with tracer.start_span('get_stif_number', child_of=request.span):
            try:
                stif_number = get_stif_number(
                    controller.instance.virtual_router.router,
                    'iaas_vpn_create_002',
                )
            except IAASException as e:
                return Http400(error_code=e.args[0])

        with tracer.start_span('set_vpn_details', child_of=request.span):
            controller.instance.stif_number = stif_number
            controller.instance.send_email = True

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('generating_ike_identifiers', child_of=request.span):
            identifier = get_ike_identifier(vpn=controller.instance)
            controller.instance.ike_local_identifier = f'local-{identifier}'
            controller.instance.ike_remote_identifier = f'remote-{identifier}'
            controller.instance.save()

        with tracer.start_span('saving_routes', child_of=request.span):
            for route in routes:
                route.vpn = controller.instance
                route.save()

        num_clients = 0
        if controller.cleaned_data['vpn_type'] == VPN.DYNAMIC_SECURE_CONNECT:
            with tracer.start_span('saving_vpn_clients', child_of=request.span):
                for vpn_client in vpn_clients:
                    vpn_client.vpn = controller.instance
                    vpn_client.save()
                    num_clients += 1

        vpn_sku = skus.SITE_TO_SITE
        if controller.instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            vpn_sku = skus.DYNAMIC_SECURE_CONNECT

        with tracer.start_span('generate_vpn_history', child_of=request.span):
            VPNHistory.objects.create(
                modified_by=request.user.id,
                customer_address=controller.instance.virtual_router.project.address_id,
                project_id=controller.instance.virtual_router.project.pk,
                project_name=controller.instance.virtual_router.project.name,
                vpn=controller.instance,
                vpn_quantity=max(num_clients, 1),
                vpn_sku=vpn_sku,
            )

        with tracer.start_span('update_virtual_router_and_project', child_of=request.span):
            virtual_router = controller.instance.virtual_router
            VirtualRouter.objects.filter(pk=virtual_router.pk).update(state=states.RUNNING_UPDATE)
            virtual_router.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            data = VPNSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class VPNResource(APIView):
    """
    Handles methods regarding VPN that do require a specific id
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a VPN record by the given `pk`.
        description: Verify if a VPN record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the VPN.
                type: integer

        responses:
            200:
                description: Requested VPN exists and requesting User can access.
            404:
                description: Requesting user cannot access VPN if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VPN.objects.get(pk=pk)
            except VPN.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            error = Permissions.read(request, obj, span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read a VPN

        description: |
            Attempt to read information about a specific VPN, returning 404 if VM doesn't exist or
            403 if user doesn't have permission.

        path_params:
            pk:
                description: The id of the VPN to Read
                type: integer

        responses:
            200:
                description: The details of the specified VM
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VPN.objects.get(pk=pk)
            except VPN.DoesNotExist:
                return Http404(error_code='iaas_vpn_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        # collect email addresses only if necessary ie when send_email field is True
        if obj.send_email:
            with tracer.start_span('fetching_email_addresses', child_of=request.span) as child_span:
                manager_id = obj.virtual_router.project.manager_id
                modified_by = VPNHistory.objects.filter(vpn_id=obj.pk).order_by('-created')[0].modified_by
                params = {'search[id__in]': [modified_by, manager_id]}
                users_response = Membership.user.list(token=request.auth, params=params, span=child_span)
                emails: List[str] = []
                if users_response.status_code == 200:
                    emails = []
                    for user in users_response.json()['content']:
                        emails.append(user['email'])
                    obj.emails = emails

        with tracer.start_span('serializing_data', child_of=request.span):
            data = VPNSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the specified VPN Tunnel

        description: |
            Endpoint to update a given VPN Tunnel.

            After the update, the Virtual Router will be set to the UPDATE state to build the VPN Tunnel with the new
            details.
            As a result, this method can only be fully executed if the chosen VirtualRouter is in a state that can be
            moved to the UPDATE state.

        path_params:
            pk:
                description: The id of the VPN record to be updated
                type: integer

        responses:
            200:
                description: The updated details of the VPN record
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VPN.objects.get(pk=pk)
            except VPN.DoesNotExist:
                return Http404(error_code='iaas_vpn_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('checking_virtual_router', child_of=request.span):
            if not request.user.robot and not obj.virtual_router.can_update():
                return Http400(error_code='iaas_vpn_update_002')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VPNUpdateController(
                data=request.data,
                request=request,
                span=span,
                partial=partial,
                instance=obj,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('set_vpn_modified_by_and_send_email', child_of=request.span):
            # if user is Robot, then send_email is reset.
            if request.user.robot:
                controller.instance.send_email = False

        with tracer.start_span('saving_object', child_of=request.span):
            routes = controller.cleaned_data.pop('routes', {})
            if obj.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
                vpn_clients = controller.cleaned_data.pop('vpn_clients', {})
            controller.instance.save()

        with tracer.start_span('saving_routes', child_of=request.span):
            for route in routes:
                # If there a new route VPN has not been assigned
                route.vpn = obj
                route.save()

        num_clients = 0
        if obj.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
            with tracer.start_span('saving_vpn_clients', child_of=request.span):
                for vpn_client in vpn_clients:
                    # If there a new client VPN has not been assigned
                    vpn_client.vpn = controller.instance
                    vpn_client.save()
                    num_clients += 1

        if controller.instance.send_email:
            vpn_sku = skus.SITE_TO_SITE
            if controller.instance.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
                vpn_sku = skus.DYNAMIC_SECURE_CONNECT
            with tracer.start_span('generate_vpn_history', child_of=request.span):
                VPNHistory.objects.create(
                    modified_by=request.user.id,
                    customer_address=obj.virtual_router.project.address_id,
                    project_id=obj.virtual_router.project.pk,
                    project_name=obj.virtual_router.project.name,
                    vpn=obj,
                    vpn_quantity=max(num_clients, 1),
                    vpn_sku=vpn_sku,
                )

        with tracer.start_span('update_virtual_router_and_project', child_of=request.span):
            if not request.user.robot:
                obj.virtual_router.state = states.RUNNING_UPDATE
                obj.virtual_router.save()
                obj.virtual_router.project.set_run_robot_flags()

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            data = VPNSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Partial Update
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete the specified VPN Tunnel

        description: |
            Endpoint to delete a given VPN Tunnel.

            After deletion, the Virtual Router will be set to the UPDATE state to remove the VPN Tunnel.
            As a result, this method can only be fully executed if the chosen VirtualRouter is in a state that can be
            moved to the UPDATE state.

        path_params:
            pk:
                description: The id of the VPN record to be deleted
                type: integer

        responses:
            204:
                description: The VPN was deleted successfully.
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = VPN.objects.get(pk=pk)
            except VPN.DoesNotExist:
                return Http404(error_code='iaas_vpn_delete_001')

        with tracer.start_span('checking_virtual_router', child_of=request.span):
            if not obj.virtual_router.can_update():
                return Http400(error_code='iaas_vpn_delete_002')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.cascade_delete()

        with tracer.start_span('generate_vpn_history', child_of=request.span):
            vpn_sku = skus.SITE_TO_SITE
            if obj.vpn_type == VPN.DYNAMIC_SECURE_CONNECT:
                vpn_sku = skus.DYNAMIC_SECURE_CONNECT

            VPNHistory.objects.create(
                modified_by=request.user.id,
                customer_address=obj.virtual_router.project.address_id,
                project_id=obj.virtual_router.project.pk,
                project_name=obj.virtual_router.project.name,
                vpn=obj,
                vpn_quantity=0,
                vpn_sku=vpn_sku,
            )

        with tracer.start_span('update_virtual_router_and_project', child_of=request.span):
            obj.virtual_router.state = states.RUNNING_UPDATE
            obj.virtual_router.save()
            obj.virtual_router.project.set_run_robot_flags()

        return Response(status=status.HTTP_204_NO_CONTENT)
