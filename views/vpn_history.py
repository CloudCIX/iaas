"""
Views for VPNHistory
"""
# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import VPNHistoryListController
from iaas.models import VPNHistory
from iaas.serializers import VPNHistorySerializer
from iaas.utils import get_addresses_in_member


__all__ = [
    'VPNHistoryCollection',
]


class VPNHistoryCollection(APIView):
    """
    Handles methods regarding VPNHistoryCollection that do not require the "pk" parameter
    """
    def get(self, request: Request) -> Response:
        """
        summary: List the VPNHistory records.

        description: |
            Retrieve a list of VPNHistoryCollection records for VPNs the requesting user as access to.
            VPNHistoryCollection records are created when a VPN is created or deleted and contain details necessary
            for billing purposes.

        responses:
            200:
                description: A list of VPNHistory records for the specified VPN.
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VPNHistoryListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('applying_address_filters', child_of=request.span) as span:
            address_filtering: Optional[Q] = None
            if request.user.robot:
                address_filtering = Q(vpn__virtual_router__project__region_id=request.user.address['id'])
            elif request.user.id != 1:
                # A global-active user can list all VPN history records for customer_address in their member
                if request.user.is_global and request.user.global_active:
                    address_filtering = Q(customer_address__in=get_addresses_in_member(request, span))
                else:
                    address_filtering = Q(customer_address=request.user.address['id'])

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = VPNHistory.objects.filter(
                    **controller.cleaned_data['search'],
                )

                if address_filtering is not None:
                    objs = objs.filter(address_filtering)

                objs = objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )

            except (ValueError, ValidationError):
                return Http400(error_code='iaas_vpn_history_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'total_records': objs.count(),
                'warnings': controller.warnings,
            }
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = VPNHistorySerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})
