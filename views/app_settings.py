"""
Management of App Settings
"""
from datetime import datetime
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
# local
from iaas.controllers import AppSettingsCreateController, AppSettingsUpdateController
from iaas.models import AppSettings
from iaas.permissions.app_settings import Permissions
from iaas.serializers import AppSettingsSerializer

__all__ = [
    'AppSettingsCollection',
    'AppSettingsResource',
]


class AppSettingsCollection(APIView):
    def post(self, request: Request) -> Response:
        """
        summary: Create a new App Settings

        description: Create a new App Settings entry with data given by user

        responses:
            201:
                description: App Settings record created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('check_existing', child_of=request.span):
            if len(AppSettings.objects.filter()) > 0:
                return Http404(error_code='iaas_app_settings_create_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AppSettingsCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = AppSettingsSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AppSettingsResource(APIView):
    """
    Return an individual App Settings object.
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Retrieve details of a specific app settings record.

        description: Retrieve the details of the app settings with id 'pk'.

        path_params:
            pk:
                description: The ID of the app settings to be retrieved.
                type: integer

        responses:
            200:
                description: An app settings is returned
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request)
            if err is not None:
                return err

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = AppSettings.objects.get(
                    pk=pk,
                )
            except AppSettings.DoesNotExist:
                return Http404(error_code='iaas_app_settings_read_001')

        # Serialise the data and return.
        with tracer.start_span('serializing_data', child_of=request.span):
            data = AppSettingsSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified app settings record.

        description: Attempt to update an app settings record by the given `pk`, returning a 404 if it doesn't exist.

        path_params:
            pk:
                description: The id of the app settings record to be updated.
                type: integer

        responses:
            200:
                description: App settings record was updated successfully.
            400: {}
            403: {}
            404: {}
        """

        tracer = settings.TRACER

        # Check if primary key is valid.
        with tracer.start_span('retrieving_object', child_of=request.span):
            try:
                obj = AppSettings.objects.get(
                    pk=pk,
                )
            except AppSettings.DoesNotExist:
                return Http404(error_code='iaas_app_settings_update_001')

        # Check permissions.
        with tracer.start_span('checking_permissions', child_of=request.span):
            error = Permissions.update(request)
            if error is not None:
                return error

        # Validate controller.
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AppSettingsUpdateController(
                data=request.data,
                request=request,
                partial=partial,
                span=span,
                instance=obj,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        # Save objects.
        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        # Serialise and return the data.
        with tracer.start_span('serializing_data', child_of=request.span):
            serializer = AppSettingsSerializer(instance=controller.instance)

        return Response({'content': serializer.data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a storage type.
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified app settings record.

        description: |
            Attempt to delete an app settings record. record by the given `pk`, returning a 404 if it doesn't exist

        path_params:
            pk:
                description: The id of the app settings record to be deleted
                type: string

        responses:
            204:
                description: app settings record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = AppSettings.objects.get(id=pk)
            except AppSettings.DoesNotExist:
                return Http404(error_code='iaas_app_settings_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.deleted = datetime.utcnow()
            obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
