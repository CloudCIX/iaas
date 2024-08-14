"""
Management of Records
"""

# stdlib
import logging
from datetime import datetime
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
from iaas.controllers import (
    RecordListController,
    RecordUpdateController,
    RecordCreateController,
)
from iaas.models import Record
from iaas.permissions.record import Permissions
from iaas.serializers import RecordSerializer

__all__ = [
    'RecordCollection',
    'RecordResource',
]


class RecordCollection(APIView):
    """
    Handles methods regarding Record without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List Records
        description: |
            Retrieve a list of Records using filters sent by the User.

        responses:
            200:
                description: A list of Records
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = RecordListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of Records using filters
        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = Record.objects.filter(
                    domain__member_id=request.user.member['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_record_list_001')

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
            data = RecordSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Record entry

        description: |
            Create a new Record entry using data given by user.
            You can only create a Record for your own Member.

        responses:
            201:
                description: Record record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RecordCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('creating_object_in_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.record.create')
                data = {
                    'id': controller.instance.domain_id,
                    'name': controller.instance.name,
                    'content': controller.instance.content,
                    'type': controller.instance.type,
                    'ttl': controller.instance.time_to_live,
                    'geozone': controller.instance.georegion,
                    'priority': controller.instance.priority,
                }
                response = rage4.record_create(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('Record create: No response received from Rage4 API')
                    return Http503(error_code='iaas_record_create_001')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        'Non 200 response received from Rage4 API or "error" was in the response '
                        f'({response.content.decode()}) for data: {data}',
                    )
                    return Http503(error_code='iaas_record_create_002')

                controller.instance.id = rage4_response['id']
        else:
            # Assign a random ID for staging purposes
            controller.instance.id = Record.get_random_id()

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class RecordResource(APIView):
    """
    Handles methods regarding Record records that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a Record record by the given `pk`.
        description: Verify if a Record record by the given `pk` exists and requesting User is alllowed to access.

        path_params:
            pk:
                description: The ID of the Record.
                type: integer

        responses:
            200:
                description: Requested Record exists and requesting User can access.
            404:
                description: Requesting user cannot access Record if it exists.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Record.objects.get(pk=pk)
            except Record.DoesNotExist:
                return Http404()

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.read(request, obj)
            if error is not None:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified Record record

        description: |
            Attempt to read a Record record by the given `id`, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Record record to be read
                type: integer

        responses:
            200:
                description: Record record was read successfully
            403: {}
            404: {}
            503:
                description: An error occurred when attempting to create the Record in the Rage4 API
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Record.objects.get(id=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_record_read_001')

        # Check permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified Record record

        description: |
            Attempt to update a Record record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Record to be updated
                type: integer

        responses:
            200:
                description: Record record was updated successfully
            400: {}
            403: {}
            404: {}
            503:
                description: An error occurred when attempting to update the Record in the Rage4 API
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Record.objects.get(id=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_record_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RecordUpdateController(instance=obj, data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('updating_object_in_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.record.update')
                data = {
                    'id': controller.instance.pk,
                    'name': controller.instance.name,
                    'content': controller.instance.content,
                    'ttl': controller.instance.time_to_live,
                    'geozone': controller.instance.georegion,
                    'priority': controller.instance.priority,
                    'type': obj.type,
                }
                response = rage4.record_update(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('Record update: No response received from Rage4 API')
                    return Http503(error_code='iaas_record_update_002')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        f'Non 200 response received from Rage4 API or "error" was in the response for record #{obj.pk}'
                        f'({response.content.decode()}) for data: {data}',
                    )
                    return Http503(error_code='iaas_record_update_003')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Record record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Record record

        description: |
            Attempt to delete a Record record by the given `id`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the Record to be deleted
                type: string

        responses:
            204:
                description: Record record was deleted successfully
            403: {}
            404: {}
            503:
                description: An error occurred when attempting to delete the Record in the Rage4 API
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Error'
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Record.objects.get(id=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_record_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('deleting_object_from_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.record.delete')
                data = {
                    'id': obj.pk,
                }
                response = rage4.record_delete(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('Record delete: No response received from Rage4 API')
                    return Http503(error_code='iaas_record_delete_002')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        f'Non 200 response received from Rage4 API or "error" was in the response for record #{obj.pk}'
                        f'({response.content.decode()})',
                    )
                    return Http503(error_code='iaas_record_delete_003')

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.utcnow()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
