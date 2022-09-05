"""
Management of Subnets
"""
# stdlib
from typing import Optional, Set
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http400, Http403, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from jaeger_client import Span
from netaddr import IPSet, IPNetwork
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import (
    SubnetListController,
    SubnetUpdateController,
    SubnetCreateController,
    SubnetSpaceListController,
)
from iaas.models import (
    Allocation,
    ASN,
    Project,
    Subnet,
)
from iaas.permissions.subnet import Permissions
from iaas.serializers import SubnetSerializer, SubnetSpaceSerializer

__all__ = [
    'SubnetCollection',
    'SubnetResource',
    'SubnetSpaceCollection',
]


class IPNetworkWithSubnet(IPNetwork):
    __slots__ = list(IPNetwork.__slots__) + ['subnet_object']


class SubnetCollection(APIView):
    """
    Handles methods regarding Subnet without ID being specified
    """

    @staticmethod
    def _fetch_addresses(request: Request, span: Span) -> Set[int]:
        """
        Given a request object, retrieve all of the addresses needed to list Subnet records.
        The addresses required are as follows;
            - Addresses of non self-managed partner Members
            - Addresses of the User's Member if the User is acting global
        """
        ids: Set[int] = set()

        # Fetch non-self-managed partner addresses
        with settings.TRACER.start_span('fetching_partner_addresses', child_of=span) as child_span:
            params = {'search[member__self_managed]': False, 'limit': 100, 'page': 0}
            # This one requires a loop to go through each page to get all the results
            total_records = float('inf')
            while len(ids) < total_records:
                response = Membership.address.list(
                    token=request.auth,
                    params=params,
                    span=child_span,
                )
                if response.status_code != 200:  # pragma: no cover
                    raise Exception
                response_data = response.json()
                ids.update(address['id'] for address in response_data['content'])
                if total_records == float('inf'):
                    total_records = response_data['_metadata']['total_records']

                # Update the page value
                params['page'] += 1

        # If the User is global, also fetch the other Addresses in the Member
        if request.user.is_global:
            with settings.TRACER.start_span('fetching_member_addresses', child_of=span) as child_span:
                params = {'search[member_id]': request.user.member['id']}
                response = Membership.address.list(
                    token=request.auth,
                    params=params,
                    span=child_span,
                )
                if response.status_code != 200:  # pragma: no cover
                    raise Exception
                ids.update(address['id'] for address in response.json()['content'])

        # Finally, add the User's Address id
        ids.add(request.user.address['id'])

        return ids

    def get(self, request: Request) -> Response:
        """
        summary: List Subnets
        description: |
            Retrieve a list of Subnets.
            The list of Subnets is pre-filtered to also return Subnets that match the following pre-requisites;
                - The parent ASN is owned by your Member.
                - The parent Allocation is owned by your Address.
                - The parent Subnet is owned by your Address.
                - The Subnet is owned by a non self managed partner Member

            Subnets that are owned by your Address ID are also returned in the list.

        responses:
            200:
                description: A list of Subnets
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = SubnetListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of Subnets using filters
        with tracer.start_span('get_objects', child_of=request.span) as span:
            with tracer.start_span('fetch_addresses', child_of=span) as child_span:
                try:
                    address_ids = SubnetCollection._fetch_addresses(request, child_span)
                except Exception:  # pragma: no cover
                    return Http403(error_code='iaas_subnet_list_001')

            # Handle the robot filtering by setting up extra filters for Subnets in the cloud
            robot_filtering: Optional[Q] = None
            # If the request comes from a Robot get a list of asn numbers for projects in their region
            if request.user.robot:
                project_ids = Project.objects.filter(region_id=request.user.address['id']).values_list('pk', flat=True)
                robot_filtering = Q(allocation__asn__number__in=[(id + ASN.pseudo_asn_offset) for id in project_ids])

            with tracer.start_span('query_db', child_of=span):
                q = (
                    Q(allocation__asn__member_id=request.user.member['id'])
                    | Q(allocation__address_id=request.user.address['id'])
                    | Q(parent__address_id=request.user.address['id'])
                    | Q(address_id__in=address_ids)
                )
                if robot_filtering is not None:
                    q = q | robot_filtering
                try:
                    objs = Subnet.objects.filter(
                        q,
                        **controller.cleaned_data['search'],
                    ).exclude(
                        **controller.cleaned_data['exclude'],
                    ).order_by(
                        controller.cleaned_data['order'],
                    )
                except (ValueError, ValidationError):
                    return Http400(error_code='iaas_subnet_list_002')

        with tracer.start_span('generating_metadata', child_of=request.span):
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
            # Handle pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = SubnetSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Subnet entry

        description: |
            Create a new Subnet entry using data given by user.

            There are a couple of different ways to create a Subnet;
                - Create a Subnet as the child of an Allocation record, by sending `allocation_id`.
                - Create a Subnet as the child of another Subnet, by sending `subnet_id`.
                - Create a Subnet for the cloud by sending the `cloud` flag as True and the ID of a Virtual Router.

        responses:
            201:
                description: Subnet record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SubnetCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SubnetSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class SubnetResource(APIView):
    """
    Handles methods regarding Subnet records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Subnet record by the given `pk`.
        description: Verify if a Subnet record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Subnet.
                type: integer

        responses:
            200:
                description: Requested Subnet exists and requesting User can access.
            404:
                description: Requesting user cannot access Subnet if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Subnet.objects.get(pk=pk)
            except Subnet.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span) as child_span:
            error = Permissions.head(request, obj, child_span)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified Subnet record

        description: |
            Attempt to read a Subnet record by the given `pk`, returning a 404 if it does not exist.

        path_params:
            pk:
                description: The id of the Subnet record to be read.
                type: integer

        responses:
            200:
                description: Subnet record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Subnet.objects.get(pk=pk)
            except Subnet.DoesNotExist:
                return Http404(error_code='iaas_subnet_read_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span) as child_span:
            err = Permissions.read(request, obj, child_span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SubnetSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified Subnet record

        description: |
            Attempt to update a Subnet record by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Subnet to be updated.
                type: integer

        responses:
            200:
                description: Subnet record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Subnet.objects.get(pk=pk)
            except Subnet.DoesNotExist:
                return Http404(error_code='iaas_subnet_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as child_span:
            err = Permissions.update(request, obj, child_span)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SubnetUpdateController(
                instance=obj,
                data=request.data,
                partial=partial,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = SubnetSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Subnet record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Subnet record

        description: |
            Attempt to delete a Subnet record by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Subnet to be deleted
                type: integer

        responses:
            204:
                description: Subnet record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Subnet.objects.get(pk=pk)
            except Subnet.DoesNotExist:
                return Http404(error_code='iaas_subnet_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as child_span:
            err = Permissions.delete(request, obj, child_span)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=child_span):
            obj.cascade_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubnetSpaceCollection(APIView):

    def respond(self, request, controller, objs):
        """
        Given list of subnet objects and the controller serialize the objects and return subnet space list
        """

        tracer = settings.TRACER

        with tracer.start_span('generating_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'page': page,
                'limit': limit,
                'total_records': len(objs),
                'warnings': warnings,
            }

        response_data = list()
        with tracer.start_span('setting_response_data', child_of=request.span):
            for obj in objs[page * limit:(page + 1) * limit]:
                if hasattr(obj, 'subnet_object'):
                    obj = obj.subnet_object
                if isinstance(obj, Subnet):
                    obj = obj
                else:
                    obj = Subnet(address_range=str(obj))

                response_data.append(obj)

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(response_data))
            data = SubnetSpaceSerializer(instance=response_data, many=True).data
        return Response({'content': data, '_metadata': metadata})

    def get(self, request, allocation_id, *args, **kwargs):
        """
        summary: List Subnet space in Allocation.

        description: Retrieve a list of Subnet space used and available in an Allocation.

        path_params:
            allocation_id:
                description: The id of the Allocation to retrieve subnet space information for
                type: integer

        responses:
            200:
                description: A list of Subnet Space in given allocation
            400: {}
        """
        tracer = settings.TRACER

        kw = {}
        with tracer.start_span('set_filters_by_member_id', child_of=request.span):
            if request.user.member['id'] != 1:
                kw['asn__member_id'] = request.user.member['id']

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                allocation = Allocation.objects.get(id=allocation_id, **kw)
            except Allocation.DoesNotExist:
                return Http400(error_code='iaas_subnet_space_list_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = SubnetSpaceListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        space_type = controller.cleaned_data['search'].get('space_type', 'all')
        objs = allocation.subnets.filter()

        # existing was sent as value for space_type - return list of existing subnets in allocation
        if space_type == 'existing':
            return self.respond(request, controller, objs)

        taken = list()
        with tracer.start_span('set_existing_subnets', child_of=request.span) as span:
            for obj in objs:
                network = IPNetworkWithSubnet(obj.address_range)
                network.subnet_object = obj
                taken.append(network)

        taken_set = IPSet(taken)

        with tracer.start_span('set_free_subnets', child_of=request.span) as span:
            free = IPSet([allocation.address_range]) ^ taken_set
            objs = [IPNetwork(n) for n in free.iter_cidrs()]

        if space_type == 'free':
            return self.respond(request, controller, objs)

        objs.extend(taken)
        objs = sorted(objs)
        return self.respond(request, controller, objs)
