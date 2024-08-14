"""
The Cloud Service is a one stop endpoint to safely create an entire cloud Project in a single request, instead of
interacting with the various other services individually.

The biggest benefit of this approach is that nothing will be created in hardware unless the entire request is
successful, which would not be possible via the individual services themselves.
"""
# stdlib
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas import state as states
from iaas.controllers import CloudCreateController, CloudUpdateController
from iaas.models import Project, Server
from iaas.permissions.cloud import Permissions
from iaas.serializers import CloudSerializer

__all__ = [
    'CloudCollection',
    'CloudResource',
]


class CloudCollection(APIView):
    """
    Manage methods related to Cloud that don't require an id to be sent.
    """

    def post(self, request: Request) -> Response:
        """
        summary: Create a full Cloud Project in a single request.

        description: |
            Safely create a full Cloud Project using a single API request.

            This method is described as "safe" because the Project will only be fully created if and only if the
            entirety of the data sent is valid.
            Any invalid data will cause the whole request to fail, and no infrastructure will be built accidentally.

        responses:
            201:
              description: Successfully created the Cloud Project
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

                          In the case of any field that is sent to this endpoint as an array of objects that contains
                          errors, the field will be returned as an array if no errors were found with the array being
                          sent.
                          This array will contain error objects in the positions that match the positions of the
                          object(s) that caused errors, and null in positions that are okay.

                          In the case that the fields that are meant to be an array are invalid (i.e. not an array), the
                          returned item for that field will be a single Error object instead.

                        required:
                          - errors
                        properties:
                          errors:
                            type: object
                            properties:
                              project:
                                $ref: '#/components/schemas/Error'
                              subnets:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
                              vms:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
                              firewall_rules:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CloudCreateController(
                request=request,
                data=request.data,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            # Call save on the controller, which will handle updating the states and saving them
            controller.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            # Serializer the controller since that has all the fields needed
            data = CloudSerializer(controller).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CloudResource(APIView):
    """
    Manage methods related to Cloud that require an id to be sent.
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the full details of a Cloud Project in a single request.

        description: |
            Read a full Cloud Project using a single API request.

            This method operates like Project.read except it returns everything about a Project, including VMs, VPNs,
            etc.

        path_params:
            pk:
                description: The ID of the Project to use to read for this method
                type: integer

        responses:
            200:
                description: The full details of the Cloud Project.
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                project = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_cloud_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, project, span)
            if err is not None:
                return err

        with tracer.start_span('fetching_virtual_router', child_of=request.span):
            virtual_router = project.virtual_router

        with tracer.start_span('fetching_vms', child_of=request.span):
            vms = project.vms.exclude(state=states.CLOSED)
            if request.user.id != 1:
                vms = vms.exclude(image__public=False)
            for vm in vms:
                server = Server.objects.get(pk=vm.server_id)
                vm.storage_type = server.storage_type.name

        with tracer.start_span('serializing_data', child_of=request.span):
            obj_data = {
                'project': project,
                'virtual_router': virtual_router,
                'vms': vms,
            }
            obj = type('cloud', (object,), obj_data)
            data = CloudSerializer(obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int) -> Response:
        """
        summary: Update a full Cloud Project in a single request.

        description: |
            Safely update a full Cloud Project using a single API request.

            This method is described as "safe" because infrastructure will only be updated if the entirety of the sent
            data is valid.
            Any invalid data will cause the whole request to fail.

            This method is used to update the whole Project, which includes being able to update existing infrastructure
            as well as adding new infrastructure to an existing Project.
            In order for the method to determine what is new and what isn't, please ensure the `id` field is sent and
            valid for all existing infrastructure.

            If there is a failure during fetching of some necessary information for serializing the system, the response
            will be empty, but the updates will still have occurred.

        path_params:
            pk:
                description: The ID of the Project to use to read for this method
                type: integer

        responses:
            200:
              description: Successfully updated the Cloud Project
              content: {}
            400:
              description: Input data was invalid
              content:
                application/json:
                  schema:
                    oneOf:
                      - $ref: '#/components/schemas/Error'
                      # Define the special version of multi error that may contain an array of errors
                      - type: object
                        description: |
                          A map of field names to Error objects representing an error that was found with the
                          data supplied for that field.

                          In the case of any field that is sent to this endpoint as an array of objects that contains
                          errors, the field will be returned as an array if no errors were found with the array being
                          sent.
                          This array will contain error objects in the positions that match the positions of the
                          object(s) that caused errors, and null in positions that are okay.

                          In the case that the fields that are meant to be an array are invalid (i.e. not an array), the
                          returned item for that field will be a single Error object instead.

                        required:
                          - errors
                        properties:
                          errors:
                            type: object
                            properties:
                              project:
                                $ref: '#/components/schemas/Error'
                              subnets:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
                              vms:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
                              firewall_rules:
                                oneOf:
                                  - $ref: '#/components/schemas/Error'
                                  - type: array
                                    items:
                                      $ref: '#/components/schemas/Error'
                                      nullable: true
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_cloud_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        # Check that the existing stateful objects can be updated
        with tracer.start_span('check_update', child_of=request.span):
            # Check the VirtualRouter
            if not obj.virtual_router.can_update():
                return Http400(error_code='iaas_cloud_update_002')

            # Check the VMs - only update if all VMs are in a "Stable State"
            if obj.vms.exclude(state__in=states.STABLE_STATES).exists():
                return Http400(error_code='iaas_cloud_update_003')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CloudUpdateController(
                request=request,
                data=request.data,
                span=span,
                project=obj,
                virtual_router=obj.virtual_router,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            # Call save on the controller, which will handle updating the states and saving them
            controller.save()

        # Empty Response - Don't bother dealing with returning the details to keep things a little less complex
        return Response()
