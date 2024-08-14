"""
Manages linking two resources together
Does not have its own DB model
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.models import (
    Resource,
    VM,
)
from iaas import state as states
from iaas.permissions.attach import Permissions
from iaas.resource_type import RESOURCE_COMPAT_MAP

__all__ = [
    'AttachResource',
]


class AttachResource(APIView):
    """
    Handles methods regarding Resource records that require ID to be specified
    """

    def put(self, request: Request, resource_id: int, parent_resource_id: int) -> Response:
        """
        summary: Attach one Resource to another
        description: |
            Assign one Resource as the parent of another Resource.
            A Resource is Attached if it has a parent_id and is in the Running state.

        path_params:
            resource_id:
                description: The ID of the child Resource
                type: integer
            parent_resource_id:
                description: The ID of the parent Resource
                type: integer

        responses:
            200:
                description: Resources were attached successfully
                content:
                    application/json:
                        schema:
                            type: object
            400: {}
            403: {}
            404:
                description: Requesting user cannot access Resources
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_child_object', child_of=request.span):
            try:
                child = Resource.objects.get(
                    id=resource_id,
                    project__address_id=request.user.address['id'],
                )
            except Resource.DoesNotExist:
                return Http404(error_code='iaas_attach_update_001')

            if child.resource_type not in RESOURCE_COMPAT_MAP:
                return Http400(error_code='iaas_attach_update_002')

            if child.parent_id is not None:
                return Http400(error_code='iaas_attach_update_003')

            if child.state not in [states.RUNNING, states.QUIESCED]:
                return Http400(error_code='iaas_attach_update_004')

        with tracer.start_span('retrieving_parent_object', child_of=request.span):
            try:
                parent = VM.objects.get(
                    id=parent_resource_id,
                    project__address_id=request.user.address['id'],
                )
            except VM.DoesNotExist:
                return Http404(error_code='iaas_attach_update_005')

            if child.project_id != parent.project_id:
                return Http400(error_code='iaas_attach_update_006')

            if parent.state not in [states.RUNNING, states.QUIESCED]:
                return Http400(error_code='iaas_attach_update_007')

        with tracer.start_span('attaching_resources'):
            self.attach_resources(child, parent)

        with tracer.start_span('setting_run_robot'):
            parent.project.set_run_robot_flags()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def attach_resources(child_resource, parent_resource):
        """
        Put the child in the Running state and set its parent_id
        Put the parent in an Updating state, depending on its current state
        """
        child_resource.parent_id = parent_resource.id
        child_resource.state = states.RUNNING
        child_resource.save()

        # Put the parent into an updating state
        if parent_resource.state is states.RUNNING:
            parent_resource.state = states.RUNNING_UPDATE
        else:
            parent_resource.state = states.QUIESCED_UPDATE
        parent_resource.save()
