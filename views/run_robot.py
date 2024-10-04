"""
Management of Run Robot
"""
# python
from copy import deepcopy
from typing import Any, Dict
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import RunRobotTurnOffController
from iaas.models import Backup, Project, ServerType, Snapshot, VirtualRouter, VM
from iaas.models.resource import Resource, ResourceManager
from iaas.permissions.run_robot import Permissions
import iaas.state as states
from iaas.utils import get_region_cache_key


__all__ = [
    'RunRobotCollection',
]

DRIVER_METHODS_DICT: Dict[str, Any] = {
    # Driver response
    'build': [],
    'quiesce': [],
    'restart': [],
    'scrub': [],
    'scrubprep': [],
    'updatequiesced': [],
    'updaterunning': [],
    # Required methods for current version response
    'quiesced_update': [],
    'running_update': [],
}

VM_KVM_SERVERS = [ServerType.KVM, ServerType.GPU_A100, ServerType.GPU_H100]


def _get_objs_to_process(obj_model, project_ids, servers=None, phantom=False):
    if servers is None:
        servers = list()

    if obj_model in (Snapshot, Backup):
        objs = obj_model.objects.filter(
            vm__project_id__in=project_ids,
            vm__server__type_id__in=servers,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated')
    elif obj_model == VirtualRouter:
        objs = obj_model.objects.filter(
            router__capacity__isnull=phantom,
            project_id__in=project_ids,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated')
    elif obj_model == VM:
        objs = obj_model.objects.filter(
            project_id__in=project_ids,
            server__type_id__in=servers,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated')
    elif isinstance(obj_model, ResourceManager):
        objs = obj_model.filter(
            project_id__in=project_ids,
            state__in=states.ROBOT_PROCESS_STATES,
        ).order_by('updated')

    obj_dict = deepcopy(DRIVER_METHODS_DICT)

    for o in objs:
        if o.state == states.REQUESTED:
            obj_dict['build'].append(o.pk)
        elif o.state == states.QUIESCE:
            obj_dict['quiesce'].append(o.pk)
        elif o.state == states.RESTART:
            obj_dict['restart'].append(o.pk)
        elif o.state == states.SCRUB:
            if obj_model in (VirtualRouter, VM):
                obj_dict['scrubprep'].append(o.pk)
            # current version of robot expects these in scrub dict - the driver version should catch mismatch of
            # states and not process the overlap of ids in scrub and scrubprep lists.
            # Place in else block when only driver architecture response is supported
            obj_dict['scrub'].append(o.pk)
        elif o.state == states.SCRUB_QUEUE:
            if o.scrub_queue_time_passed:
                obj_dict['scrub'].append(o.pk)
        elif o.state == states.QUIESCED_UPDATE:
            obj_dict['updatequiesced'].append(o.pk)
        elif o.state == states.RUNNING_UPDATE:
            obj_dict['updaterunning'].append(o.pk)

    obj_dict['quiesced_update'] = obj_dict['updatequiesced']
    obj_dict['running_update'] = obj_dict['updaterunning']

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
            From Project IDs return a list of backups, ceph_drives, snapshots, virtual routers and vms that are in
            "Robot Process" states and split lists based on state.

            "Robot Process" states are Request, Running Update, Restart, Quiesce, Quiesced Update, Scrub and Scrub Prep.

        responses:
            200:
                description: A list of Project IDs and each resource to be processed as an object.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                resource:
                                    type: object
                                    properties:
                                        build:
                                            description: A list of Resource IDs in build request state
                                            type: List[integer]
                                        quiesce:
                                            description: A list of Resource IDs in quiesce request state
                                            type: List[integer]
                                        restart':
                                            description: A list of Resource IDs in restart request state
                                            type: List[integer]
                                        scrub:
                                            description: A list of Resource IDs in scrub request state
                                            type: List[integer]
                                        scrubprep:
                                            description: A list of Resource IDs in scrubprep request state
                                            type: List[integer]
                                        updatequiesced:
                                            description: A list of Resource IDs in updatequiesced request state
                                            type: List[integer]
                                        updaterunning:
                                            description: A list of Resource IDs in updaterunning request state
                                            type: List[integer]
                                        quiesced_update:
                                            description: A list of Resource IDs in updatequiesced request state
                                            type: List[integer]
                                        running_update:
                                            description: A list of Resource IDs in updaterunning request state
                                            type: List[integer]
                                project_ids:
                                    description: |
                                        A list of project ids that have virtual infrastructure in a robot process state.
                                    type: List[integer]
            403: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request)
            if err is not None:
                return err

        with tracer.start_span('creating_response_obj', child_of=request.span):
            driver_dict = deepcopy(DRIVER_METHODS_DICT)
            response = {
                # Driver response
                'project_ids': [],
                'resource': {
                    'backup_hyperv': driver_dict,
                    'backup_kvm': driver_dict,
                    'ceph': driver_dict,
                    'gpu': driver_dict,
                    'snapshot_hyperv': driver_dict,
                    'snapshot_kvm': driver_dict,
                    'virtual_router': driver_dict,
                    'virtual_router_phantom': driver_dict,
                    'vm_hyperv': driver_dict,
                    'vm_kvm': driver_dict,
                    'vm_phantom': driver_dict,
                },
                # Required resource names for current version response
                'backups': driver_dict,
                'snapshots': driver_dict,
                'virtual_routers': driver_dict,
                'vms': driver_dict,
            }

        with tracer.start_span('checking_run_robot_cache_flag', child_of=request.span):
            cache_key = get_region_cache_key(request.user.address['id'])
            run_robot_cache_true = cache.get(cache_key, True)
            # setting/creating cache for run_robot to False until another change is made
            cache.set(cache_key, False)

        with tracer.start_span('get_project_ids_by_filtering', child_of=request.span):
            project_filtering = Q(vms__state=states.SCRUB_PREP) | Q(virtual_router__state=states.SCRUB_PREP)
            if run_robot_cache_true:
                # Only apply this as an OR filter if cache was True - prevent objs being processed twice
                project_filtering = project_filtering | Q(run_robot=True)
            # Are there resources in the scrub queue
            response['project_ids'] = project_ids = Project.objects.filter(
                project_filtering,
                region_id=request.user.address['id'],
            ).order_by('updated').values_list('pk', flat=True)
            if len(project_ids) == 0:
                # No resouces to process
                return Response({'content': response})

        with tracer.start_span('get_virtual_routers_to_process', child_of=request.span):

            virtual_router = _get_objs_to_process(VirtualRouter, project_ids)
            response['resource']['virtual_router'] = virtual_router
            virtual_router_phantom = _get_objs_to_process(VirtualRouter, project_ids, phantom=True)
            response['resource']['virtual_router_phantom'] = virtual_router_phantom
            # Required resource key for current version response
            response['virtual_routers'] = {
                key: virtual_router.get(key) + virtual_router_phantom.get(key)
                for key in set(virtual_router) | set(virtual_router_phantom)
            }

        with tracer.start_span('get_vms_to_process', child_of=request.span):
            vm_hyperv = _get_objs_to_process(VM, project_ids, servers=[ServerType.HYPERV])
            response['resource']['vm_hyperv'] = vm_hyperv
            vm_kvm = _get_objs_to_process(VM, project_ids, servers=VM_KVM_SERVERS)
            response['resource']['vm_kvm'] = vm_kvm
            vm_phantom = _get_objs_to_process(VM, project_ids, servers=[ServerType.PHANTOM])
            response['resource']['vm_phantom'] = vm_phantom
            # Required resource key for current version response
            response['vms'] = {
                key: vm_hyperv.get(key) + vm_kvm.get(key) + vm_phantom.get(key)
                for key in set(vm_hyperv) | set(vm_kvm) | set(vm_phantom)
            }

        with tracer.start_span('get_snapshots_to_process', child_of=request.span):
            if run_robot_cache_true:
                snapshot_hyperv = _get_objs_to_process(Snapshot, project_ids, servers=[ServerType.HYPERV])
                response['resource']['snapshot_hyperv'] = snapshot_hyperv
                snapshot_kvm = _get_objs_to_process(Snapshot, project_ids, servers=VM_KVM_SERVERS)
                response['resource']['snapshot_kvm'] = snapshot_kvm
                # Required resource key for current version response
                response['snapshots'] = {
                    key: snapshot_hyperv.get(key) + snapshot_kvm.get(key)
                    for key in set(snapshot_hyperv) | set(snapshot_kvm)
                }

        with tracer.start_span('get_backups_to_process', child_of=request.span):
            if run_robot_cache_true:
                backup_hyperv = _get_objs_to_process(Backup, project_ids, servers=[ServerType.HYPERV])
                response['resource']['backup_hyperv'] = backup_hyperv
                backup_kvm = _get_objs_to_process(Backup, project_ids, servers=VM_KVM_SERVERS)
                backup_kvm = response['resource']['backup_kvm'] = backup_kvm
                # Required resource key for current version response
                response['backups'] = {
                    key: backup_hyperv.get(key) + backup_kvm.get(key)
                    for key in set(backup_hyperv) | set(backup_kvm)
                }

        with tracer.start_span('get_resources_to_process', child_of=request.span):
            if run_robot_cache_true:
                response['resource']['ceph'] = _get_objs_to_process(Resource.cephs, project_ids)

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
