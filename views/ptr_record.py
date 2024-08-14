"""
Management of PTR Records
"""

# stdlib
import logging
from datetime import datetime
# libs
import netaddr
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
    PTRRecordListController,
    PTRRecordUpdateController,
    PTRRecordCreateController,
)
from iaas.models import Record
from iaas.permissions.ptr_record import Permissions
from iaas.serializers import RecordSerializer

__all__ = [
    'PTRRecordCollection',
    'PTRRecordResource',
]


class PTRRecordCollection(APIView):
    """
    Handles methods regarding PTRRecord without ID being specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: List PTRRecords
        description: |
            Retrieve a list of PTR Records.
            PTR Records are handled differently due to needing to use different endpoints of the Rage4 DNS API.
            Therefore, iaas has a different end point for dealing solely with PTR Records.

        responses:
            200:
                description: A list of PTRRecords
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/RecordList'
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = PTRRecordListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        # Get a list of PTRRecords using filters
        with tracer.start_span('get_objects', child_of=request.span):
            try:
                objs = Record.ptr_objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='iaas_ptr_record_list_001')

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
        summary: Create a new PTRRecord entry

        description: |
            Create a new PTRRecord entry using data given by user.
            PTR Records are handled differently due to needing to use different endpoints of the Rage4 DNS API.
            Therefore, iaas has a different end point for dealing solely with PTR Records.

        responses:
            201:
                description: PTRRecord record was created successfully
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/RecordResponse'
            400: {}
            403: {}
            503:
                description: An error occurred when attempting to create the Record in the Rage4 API
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
            controller = PTRRecordCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Generate the domain name for the PTR Domain
        with tracer.start_span('generating_domain_name', child_of=request.span):
            ip = netaddr.IPAddress(controller.cleaned_data['ip_address'])
            reverse_ip = ip.reverse_dns.rstrip('.')
            domain_name = reverse_ip.split('.')
            if ip.version == 4:
                domain_name = '.'.join(domain_name[1:])
                subnet_mask = 24
            elif ip.version == 6:
                domain_name = '.'.join(domain_name[20:])
                subnet_mask = 48

        with tracer.start_span('controller_instance_fields', child_of=request.span):
            controller.instance.name = reverse_ip
            controller.instance.georegion = Record.GLOBAL
            controller.instance.priority = 1
            controller.instance.type = Record.PTR

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            # Check rage4 for the domain, if one doesn't exist then create one
            # We don't need a local domain for the Records (because that was how it was done a long time ago and
            # undoing that is too much effort)
            with tracer.start_span('creating_object_in_rage4', child_of=request.span) as span:
                logger = logging.getLogger('iaas.views.ptr_record.create')
                # Search for the domain with the generated name in rage4
                with tracer.start_span('finding_domain', child_of=span):
                    response = rage4.domain_list()
                    try:
                        rage4_response = response.json()
                    except (AttributeError, ValueError):
                        logger.error('Domain List: No response received from Rage4 API')
                        return Http503(error_code='iaas_ptr_record_create_001')
                    if response.status_code != 200:
                        # Request to Rage4 will return a 200 response.status_code if list was successful
                        logger.error(
                            'Non 200 response received from Rage4 API or "error" was in the response for domain_list. '
                            f'({response.content.decode()})',
                        )
                        return Http503(error_code='iaas_ptr_record_create_002')

                    domains = filter(lambda domain: domain['name'] == domain_name, rage4_response)

                try:
                    domain = next(domains)
                    domain_id = domain['id']
                except StopIteration:
                    # Create a new Domain
                    with tracer.start_span('creating_new_domain', child_of=span):
                        data = {'name': domain_name, 'subnet': subnet_mask}
                        response = rage4.domain_create(data)
                        try:
                            rage4_response = response.json()
                        except (AttributeError, ValueError):
                            logger.error('Reverse Domain create: No response received from Rage4 API')
                            return Http503(error_code='iaas_ptr_record_create_003')
                        if response.status_code != 200 or not rage4_response.get('status'):
                            # Request to Rage4 will return a 200 response.status_code. status will be False if request
                            # fails
                            # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                            # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                            logger.error(
                                'Non 200 response received from Rage4 API or "error" was in the response for '
                                f'domain_create. ({response.content.decode()}) for data {data}',
                            )
                            return Http503(error_code='iaas_ptr_record_create_004')

                        domain_id = rage4_response['id']

                # Use the Domain (either pre-existing or newly created) to create the record in the API
                with tracer.start_span('creating_ptr_record', child_of=span):
                    data = {
                        'id': domain_id,
                        'content': controller.cleaned_data['content'],
                        'geozone': controller.instance.georegion,
                        'name': controller.instance.name,
                        'priority': controller.instance.priority,
                        'ttl': controller.cleaned_data['time_to_live'],
                        'type': controller.instance.type,
                    }
                    response = rage4.record_create(data)
                    try:
                        rage4_response = response.json()
                    except (AttributeError, ValueError):
                        logger.error('PTR Record create: No response received from Rage4 API')
                        return Http503(error_code='iaas_ptr_record_create_005')
                    if response.status_code != 200 or not rage4_response.get('status'):
                        # Request to Rage4 will return a 200 response.status_code. status will be False if request
                        # fails
                        # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                        # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                        logger.error(
                            'Non 200 response received from Rage4 API or "error" was in the response for '
                            f'creating_ptr_record. ({response.content.decode()}) for domain_id #{domain_id} with data '
                            f'{data}',
                        )
                        return Http503(error_code='iaas_ptr_record_create_006')
                    controller.instance.id = rage4_response['id']

        else:
            # Just generate a random id and save it so we can use stage properly
            controller.instance.id = Record.get_random_id()

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.member_id = request.user.member['id']
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class PTRRecordResource(APIView):
    """
    Handles methods regarding PTRRecord PTRRecords that require ID to be specified
    """

    def head(self, request: Request, pk=int) -> Response:
        """
        summary: Verify a PTRRecord record by the given `pk`.
        description: Verify if a PTRRecord record by the given `pk` exists.

        path_params:
            pk:
                description: The ID of the PTRRecord.
                type: integer

        responses:
            200:
                description: Requested PTRRecord exists.
            404:
                description: Requested PTRRecord does not exist.
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                Record.ptr_objects.get(pk=pk)
            except Record.DoesNotExist:
                return Http404()

        return Response()

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specified PTRRecord PTRRecord

        description: |
            Attempt to read a PTRRecord PTRRecord by the given `id`, returning a 404 if it does not exist.
            PTR Records are handled differently due to needing to use different endpoints of the Rage4 DNS API.
            Therefore, iaas has a different end point for dealing solely with PTR Records.

        path_params:
            pk:
                description: The id of the PTRRecord PTRRecord to be read
                type: integer

        responses:
            200:
                description: PTRRecord PTRRecord was read successfully
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/RecordResponse'
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Record.ptr_objects.get(pk=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_ptr_record_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial=False) -> Response:
        """
        summary: Update the details of a specified PTR Record.

        description: |
            Attempt to update a PTRRecord record by the given `id`, returning a 404 if it doesn't exist.
            PTR Records are handled differently due to needing to use different endpoints of the Rage4 DNS API.
            Therefore, iaas has a different end point for dealing solely with PTR Records.

        path_params:
            pk:
                description: The id of the PTRRecord to be updated
                type: integer

        responses:
            200:
                description: PTRRecord record was updated successfully
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/RecordResponse'
            400: {}
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
                obj = Record.ptr_objects.get(pk=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_ptr_record_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PTRRecordUpdateController(instance=obj, data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('updating_object_in_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.ptr_record.update')
                data = {
                    'id': controller.instance.pk,
                    'name': controller.instance.name,
                    'content': controller.instance.content,
                    'ttl': controller.instance.time_to_live,
                    'geozone': controller.instance.georegion,
                    'type': obj.type,
                }
                response = rage4.record_update(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('PTR Record update: No response received from Rage4 API')
                    return Http503(error_code='iaas_ptr_record_update_002')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        f'Non 200 response received from Rage4 API or "error" was in the response for PTR record '
                        f'#{obj.pk} ({response.content.decode()}) for data: {data}',
                    )
                    return Http503(error_code='iaas_ptr_record_update_003')

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.modified_by = request.user.id
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = RecordSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a PTRRecord record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified PTR Record.

        description: |
            Attempt to delete a PTRRecord record by the given `id`, returning a 404 if it doesn't exist.
            PTR Records are handled differently due to needing to use different endpoints of the Rage4 DNS API.
            Therefore, iaas has a different end point for dealing solely with PTR Records.

        path_params:
            pk:
                description: The id of the PTRRecord to be deleted
                type: integer

        responses:
            204:
                description: PTRRecord PTRRecord was deleted successfully
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
                obj = Record.ptr_objects.get(pk=pk)
            except Record.DoesNotExist:
                return Http404(error_code='iaas_ptr_record_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            with tracer.start_span('deleting_object_from_rage4', child_of=request.span):
                logger = logging.getLogger('iaas.views.ptr_record.delete')
                data = {
                    'id': obj.pk,
                }
                response = rage4.record_delete(data)
                try:
                    rage4_response = response.json()
                except (AttributeError, ValueError):
                    logger.error('PTR Record delete: No response received from Rage4 API')
                    return Http503(error_code='iaas_ptr_record_delete_002')
                if response.status_code != 200 or not rage4_response.get('status'):
                    # Request to Rage4 will return a 200 response.status_code. status will be False if request fails
                    # Success Request - # {'status': True, 'id': 1234, 'error': ''}
                    # Failed Request - {'status': False, 'id': 1234, 'error': 'operation failed'}
                    logger.error(
                        f'Non 200 response received from Rage4 API or "error" was in the response for PTR record '
                        f'#{obj.pk} ({response.content.decode()})',
                    )
                    return Http503(error_code='iaas_ptr_record_delete_003')

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.utcnow()
            obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
