"""
Management of Physical Routers
"""
# stdlib
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
# local
from iaas.controllers import RouterListController, RouterCreateController, RouterUpdateController
from iaas.models import IPAddress, Router, Subnet
from iaas.permissions.router import Permissions
from iaas.serializers import RouterSerializer

__all__ = [
    'RouterCollection',
    'RouterResource',
]


class RouterCollection(APIView):

    def get(self, request: Request) -> Response:
        """
        summary: List Routers

        description: |
            Retrieve a list of Routers

        responses:
            200:
                description: A list of Router records
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RouterListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:
            # Get a list of Router objects
            kw = controller.cleaned_data['search']
            if request.user.id != 1:
                kw['region_id'] = request.user.address['id']
            try:
                objs = Router.objects.filter(
                    **kw,
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_router_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span) as span:
            total_records = objs.count()
            page = controller.cleaned_data['page']
            order = controller.cleaned_data['order']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'total_records': total_records,
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]  # Handle pagination

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = RouterSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Router

        description: Create a new Router entry with data given by user

        responses:
            201:
                description: Router record created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RouterCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            public_port_ips = controller.cleaned_data.pop('public_port_ips', [])
            router_subnets = controller.cleaned_data.pop('router_subnets', [])
            controller.instance.region_id = request.user.address['id']
            controller.instance.save()

        # Update Subnets with router_id
        with tracer.start_span('saving_router_to_subnets', child_of=request.span):
            for subnet in router_subnets:
                subnet.router = controller.instance
                subnet.save()

        # Create IP Addresses for Router
        with tracer.start_span('saving_router_ips', child_of=request.span):
            ips = [
                IPAddress(router=controller.instance, modified_by=self.request.user.id, **ip)
                for ip in public_port_ips
            ]
            IPAddress.objects.bulk_create(ips)

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RouterSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class RouterResource(APIView):
    """
    Handles methods regarding Routers that require the "pk" parameter
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Router record by the given `pk`.
        description: Verify if a Router record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Router.
                type: integer

        responses:
            200:
                description: Requested Router exists and requesting User can access.
            404:
                description: Requesting user cannot access Router if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Router.objects.get(pk=pk)
            except Router.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.head(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Router

        description: |
            Attempt to read a Router by the given `pk`, returning a 404 if does not exist

        path_params:
            pk:
                description: The ID of Router to be read
                type: integer

        responses:
            200:
                description: Router was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Router.objects.get(pk=pk)
            except Router.DoesNotExist:
                return Http404(error_code='iaas_router_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RouterSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Router

        description: |
            Attempt to update a Router by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The ID of the Router to be updated
                type: integer

        responses:
            200:
                description: Router was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Router.objects.get(pk=pk)
            except Router.DoesNotExist:
                return Http404(error_code='iaas_router_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as child_span:
            controller = RouterUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                span=child_span,
                partial=partial,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            public_port_ips = controller.cleaned_data.pop('public_port_ips', [])
            router_subnets = controller.cleaned_data.pop('router_subnets', [])
            remove_subnets = controller.cleaned_data.pop('remove_subnets', [])
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        if len(public_port_ips) > 0:
            controller.instance.router_ips.all().delete()
            with tracer.start_span('saving_router_ips', child_of=request.span):
                ips = [IPAddress(router=obj, modified_by=self.request.user.id, **ip) for ip in public_port_ips]
                IPAddress.objects.bulk_create(ips)

        # Remove router_id from Subnets
        with tracer.start_span('removing_router_from_subnets', child_of=request.span):
            if len(remove_subnets) > 0:
                remove = Subnet.objects.filter(pk__in=remove_subnets)
                for subnet in remove:
                    subnet.router = None
                    subnet.modified_by = request.user.id
                    subnet.save()

        # Update Subnets with router_id
        with tracer.start_span('saving_router_to_subnets', child_of=request.span):
            if len(router_subnets) > 0:
                for subnet in router_subnets:
                    subnet.router = obj
                    subnet.modified_by = request.user.id
                    subnet.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RouterSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Router
        """
        return self.put(request, pk, True)
