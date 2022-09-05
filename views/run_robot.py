"""
Management of Run Robot
"""
# python
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import RunRobotTurnOffController
from iaas.models import Backup, Project, Snapshot, VirtualRouter, VM
from iaas.permissions.run_robot import Permissions
import iaas.state as states


__all__ = [
    'RunRobotCollection',
]


def _get_objs_to_process(obj_model, project_ids):

    if obj_model in (Snapshot, Backup):
        objs = obj_model.objects.filter(
            vm__project_id__in=project_ids,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated').values('pk', 'state')
    else:
        # Virtual Router, VM
        objs = obj_model.objects.filter(
            project_id__in=project_ids,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated').values('pk', 'state')

    obj_dict = {
        'build': [],
        'quiesce': [],
        'quiesced_update': [],
        'restart': [],
        'running_update': [],
        'scrub': [],
    }

    for o in objs:
        if o['state'] == states.REQUESTED:
            obj_dict['build'].append(o['pk'])
        elif o['state'] == states.QUIESCE:
            obj_dict['quiesce'].append(o['pk'])
        elif o['state'] == states.QUIESCED_UPDATE:
            obj_dict['quiesced_update'].append(o['pk'])
        elif o['state'] == states.RESTART:
            obj_dict['restart'].append(o['pk'])
        elif o['state'] == states.RUNNING_UPDATE:
            obj_dict['running_update'].append(o['pk'])
        elif o['state'] == states.SCRUB:
            obj_dict['scrub'].append(o['pk'])

    return obj_dict


class RunRobotCollection(APIView):
    """
    Handles methods regarding Run Robot without ID being specified
    """

    def get(self, request, *args, **kwargs):
        """
        summary: Returns a list of infrastructure for projects that robot needs to process.
        description: |
            Retrieve a list of Project ID's in robot's region that has virtual infrastructure to be processed
            From Project IDs get return a list of backups, snapshots, virtual routers and vms that are in
            "Robot Process" states and split lists based on state.

            "Robot Process" states are Request, Runnings Update, Restart, Quiesce, Quiesced Update and Scrub.
        responses:
            200:
                description: A list of Project IDs, Virtual Routers, VMs, Snapshots and Backups to be processed.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                backups:
                                    type: object
                                    properties:
                                        build:
                                            description: A list of backup ids in build request state
                                            type: List[integer]
                                        quiesce:
                                            description: A list of backup ids in quiesce request state
                                            type: List[integer]
                                        quiesced_update':
                                            description: A list of backup ids in quiesced update request state
                                            type: List[integer]
                                        restart:
                                            description: A list of backup ids in restart request state
                                            type: List[integer]
                                        running_update:
                                            description: A list of backup ids in running update request state
                                            type: List[integer]
                                        scrub:
                                            description: A list of backup ids in scrub request state
                                            type: List[integer]
                                project_ids:
                                    description: |
                                        A list of project ids that have virtual infrastruce in a robot process state.
                                    type: List[integer]
                                snapshots:
                                    type: object
                                    properties:
                                        build:
                                            description: A list of snapshot ids in build request state
                                            type: List[integer]
                                        quiesce:
                                            description: A list of snapshot ids in quiesce request state
                                            type: List[integer]
                                        quiesced_update':
                                            description: A list of snapshot ids in quiesced update request state
                                            type: List[integer]
                                        restart:
                                            description: A list of snapshot ids in restart request state
                                            type: List[integer]
                                        running_update:
                                            description: A list of snapshot ids in running update request state
                                            type: List[integer]
                                        scrub:
                                            description: A list of snapshot ids in scrub request state
                                            type: List[integer]
                                virtual_routers:
                                    type: object
                                    properties:
                                        build:
                                            description: A list of virtual router ids in build request state
                                            type: List[integer]
                                        quiesce:
                                            description: A list of virtual router ids in quiesce request state
                                            type: List[integer]
                                        quiesced_update':
                                            description: A list of virtual router ids in quiesced update request state
                                            type: List[integer]
                                        restart:
                                            description: A list of virtual router ids in restart request state
                                            type: List[integer]
                                        running_update:
                                            description: A list of virtual router ids in running update request state
                                            type: List[integer]
                                        scrub:
                                            description: A list of virtual router ids in scrub request state
                                            type: List[integer]
                                vms:
                                    type: object
                                    properties:
                                        build:
                                            description: A list of vm ids in build request state
                                            type: List[integer]
                                        quiesce:
                                            description: A list of vm ids in quiesce request state
                                            type: List[integer]
                                        quiesced_update':
                                            description: A list of vm ids in quiesced update request state
                                            type: List[integer]
                                        restart:
                                            description: A list of vm ids in restart request state
                                            type: List[integer]
                                        running_update:
                                            description: A list of vm ids in running update request state
                                            type: List[integer]
                                        scrub:
                                            description: A list of vm ids in scrub request state
                                            type: List[integer]
            403: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request)
            if err is not None:
                return err

        with tracer.start_span('checking_run_robot', child_of=request.span):
            project_ids = Project.objects.filter(
                region_id=request.user.address['id'],
                run_robot=True,
            ).order_by('updated').values_list('pk', flat=True)

        with tracer.start_span('get_virtual_routers_to_process', child_of=request.span):
            virtual_routers = _get_objs_to_process(VirtualRouter, project_ids)

        with tracer.start_span('get_vms_to_process', child_of=request.span):
            vms = _get_objs_to_process(VM, project_ids)

        with tracer.start_span('get_snapshots_to_process', child_of=request.span):
            snapshots = _get_objs_to_process(Snapshot, project_ids)

        with tracer.start_span('get_backups_to_process', child_of=request.span):
            backups = _get_objs_to_process(Backup, project_ids)

        with tracer.start_span('compiling_run_robot_response', child_of=request.span):
            response = {
                'backups': backups,
                'project_ids': project_ids,
                'snapshots': snapshots,
                'virtual_routers': virtual_routers,
                'vms': vms,
            }

        return Response({'content': response})

    def post(self, request: Request) -> Response:
        """
        summary: Turn run_robot off

        description: |
            Attempt to turn off run_robot for a list of project IDs sent in the request

        responses:
            200:
                description: run_robot was turned off for requested projects
                content: {}
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.turn_off(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RunRobotTurnOffController(
                data=request.data,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        Project.objects.filter(id__in=controller.project_ids).update(run_robot=False)

        return Response()
