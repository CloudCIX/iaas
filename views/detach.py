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
from iaas import state
from iaas.permissions.detach import Permissions
from iaas.resource_type import RESOURCE_COMPAT_MAP

__all__ = [
    'DetachResource',
]


class DetachResource(APIView):
    """
    Handles methods regarding Resource records that require ID to be specified
    """

    def put(self, request: Request, resource_id: int) -> Response:
        """
        summary: Detach a Resource from another
        description: |
            Remove the link between two Resources.
            Detach requests from the project owner marks a resource for detaching.
            A Resource marked for detaching has a parent_id and is in the Quiesced state.

            Detach requests from a robot means the resource has been detached at the hardware level.
            A detached Resource has no parent_id.

        path_params:
            resource_id:
                description: The ID of the Resource to detach
                type: integer

        responses:
            200:
                description: Resources were detached successfully
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

        with tracer.start_span('retrieving_child_object', child_of=request.span):
            address_filter = dict()
            # Robot region checks will be handled by the update permission to give more detailed information
            if not request.user.robot:
                address_filter['project__address_id'] = request.user.address_id

            try:
                obj = Resource.objects.get(
                    id=resource_id,
                    **address_filter,
                )
            except Resource.DoesNotExist:
                return Http404(error_code='iaas_detach_update_001')

        with tracer.start_span('checking permissions'):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_resource'):
            if obj.resource_type not in RESOURCE_COMPAT_MAP:
                return Http400(error_code='iaas_detach_update_002')
            if obj.parent_id is None:
                return Http400(error_code='iaas_detach_update_003')

        with tracer.start_span('detaching_resources', child_of=request.span):
            if request.user.robot:
                err = self.robot_detach(obj)
            else:
                err = self.detach(obj)
            if err is not None:
                return err

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def robot_detach(resource):
        """
        Robot has finished updating hardware
        Put the resource into the Running state and remove the parent id
        """
        if resource.state is not state.QUIESCED:
            return Http400(error_code='iaas_detach_update_004')

        resource.state = state.RUNNING
        resource.parent_id = None
        resource.save()
        return None

    @staticmethod
    def detach(resource):
        """
        User is requesting robot to update hardware
        Put the resource in the Quiesced state
        Put its parent in an Updating state
        """
        if resource.state is not state.RUNNING:
            return Http400(error_code='iaas_detach_update_005')

        # TODO: put this in a select_related when VMs are resources
        parent = VM.objects.get(id=resource.parent_id)
        if parent.state not in [state.RUNNING, state.QUIESCED]:
            return Http400(error_code='iaas_detach_update_006')

        resource.state = state.QUIESCED
        resource.save()

        # Put the parent into an updating state
        if parent.state is state.RUNNING:
            parent.state = state.RUNNING_UPDATE
        else:
            parent.state = state.QUIESCED_UPDATE
        parent.save()
        parent.project.set_run_robot_flags()
        return None
