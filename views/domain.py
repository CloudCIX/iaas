"""
Management of Domains.
Domains are handled using the Rage4 API, and can have DNS records associated with them.
"""
# stdlib
import logging
# libs
from cloudcix_rest.exceptions import Http400, Http404, Http503
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import rage4
from iaas.models import Domain
from iaas.controllers import (
    DomainListController,
    DomainCreateController,
)
from iaas.permissions.domain import Permissions
from iaas.serializers import DomainSerializer

__all__ = [
    'DomainCollection',
    'DomainResource',
]


class DomainCollection(APIView):
    """
    Handles methods regarding Domain without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Domains
        description: Retrieve a list of Domains owned by the requesting User's Member.

        responses:
            200:
                description: A list of Domains
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = DomainListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of Domains using filters
        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = Domain.objects.filter(
                    member_id=request.user.member['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_domain_list_001')

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
            data = DomainSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Domain entry

        description: Create a new Domain record using data given by User.

        responses:
            201:
                description: Domain record was created successfully
            400: {}
            403: {}
            503:
                description: An error occurred when attempting to create the Domain in the Rage4 API
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DomainCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('creating_object_in_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.domain.create')
                data = {'name': controller.instance.name}
                response = rage4.domain_create(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('Domain Create: No response received from Rage4 API')
                    return Http503(error_code='iaas_domain_create_001')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        'Non 200 response received from Rage4 API or "error" was in the response '
                        f'({response.content.decode()}) for data: {data}',
                    )
                    return Http503(error_code='iaas_domain_create_002')

                controller.instance.id = rage4_response['id']
        else:
            # Assign a random ID for staging purposes
            controller.instance.id = Domain.get_random_id()

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.member_id = request.user.member['id']
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = DomainSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class DomainResource(APIView):
    """
    Handles methods regarding Domain records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Domain record by the given `pk`.
        description: Verify if a Domain record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Domain.
                type: integer

        responses:
            200:
                description: Requested Domain exists and requesting User can access.
            404:
                description: Requesting user cannot access Domain if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Domain.objects.get(pk=pk)
            except Domain.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.read(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified Domain record

        description: |
            Attempt to read a Domain record by the given `pk`, returning a 404 if it does not exist.

        path_params:
            pk:
                description: The id of the Domain record to be read
                type: integer

        responses:
            200:
                description: Domain record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Domain.objects.get(pk=pk)
            except Domain.DoesNotExist:
                return Http404(error_code='iaas_domain_read_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = DomainSerializer(instance=obj).data

        return Response({'content': data})

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Domain record

        description: |
            Attempt to delete a Domain record by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Domain to be deleted.
                type: integer

        responses:
            204:
                description: Domain record was deleted successfully
            400: {}
            403: {}
            404: {}
            503:
                description: An error occurred when attempting to delete the Domain in the Rage4 API
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Domain.objects.get(pk=pk)
            except Domain.DoesNotExist:
                return Http404(error_code='iaas_domain_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('deleting_object_from_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.domain.delete')
                response = rage4.domain_delete(obj.pk)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('Domain delete: No response received from Rage4 API')
                    return Http503(error_code='iaas_domain_delete_002')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        f'Non 200 response received from Rage4 API or "error" was in the response for domain #{obj.pk}'
                        f'({response.content.decode()})',
                    )
                    return Http503(error_code='iaas_domain_delete_003')

        with tracer.start_span('saving_object', child_of=request.span):
            obj.cascade_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
