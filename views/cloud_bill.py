# mypy: ignore-errors
"""
Endpoint that calculates sku consumptions for all the products in a requested Project
"""
# stdlib
from datetime import datetime
from typing import Dict
# lib
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
# local
from iaas.controllers import CloudBillListController
from ..models import Project
from ..permissions.cloud_bill import Permissions
from ..utils import get_addresses_in_member

__all__ = [
    'CloudBillCollection',
    'CloudBillResource',
]


class CloudBillCollection(APIView):
    """
    Request CloudBill information for a user's addresses
    """

    def get(self, request: Request) -> Response:
        """
        summary: Get the SKU information for all the Projects the User has access to
        description: |
            For a Local User, obtain the information for all Projects in their Address.
            For a Global User, obtain the information for all Projects in Addresses in their Member.

            This information can also be filtered by `reseller_id` for more granularity.

            The data is returned in a map similar to
            ```
            {
              address_id: {
                name: 'address_name',
                data: {
                  project_id: {
                    data: {
                        product_label: {
                            state: -1,
                            created: 'timestamp',
                            skus: { sku_data },
                        }
                    },
                    name: 'project_name',
                    region_id: -1,
                    reseller_id: -1,
                },
              },
            }
            ```
            where sku_data is the same type of data that is returned from the read request below.

        parameters:
            - in: query
              name: timestamp
              schema:
                type: string
                format: date-time
              description: |
                An optional alternative timestamp to calculate hours off of, in ISO format.
                Defaults to the request time.

        responses:
            200:
                description: A set of SKUs for all the Products in the Projects of the Addresses you have access to
                content:
                    application/json:
                        schema:
                            type: object
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            # Validate using the controller
            controller = CloudBillListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('check_addresses', child_of=request.span) as span:
            # If the user is global, read their member and get all their addresses
            addresses: Dict[int, str]
            if request.user.is_global:
                span.set_tag('is_global', 'true')
                addresses = get_addresses_in_member(request, span)
            else:
                addresses = {request.user.address['id']: request.user.address['full_address']}

        # Check that if a timestamp is sent, it is valid
        with tracer.start_span('check_sent_timestamp', child_of=request.span):
            stamp_str = request.GET.get('timestamp', '')
            if stamp_str is None or str(stamp_str).strip() == '':
                timestamp = datetime.utcnow()
            else:
                # Attempt to parse the sent string
                try:
                    timestamp = datetime.fromisoformat(stamp_str)
                except ValueError:
                    return Http400(error_code='iaas_cloud_bill_list_001')

        with tracer.start_span('get_projects', child_of=request.span):
            projects = Project.objects.filter(
                address_id__in=addresses.keys(),
                **controller.cleaned_data['search'],
            )

        with tracer.start_span('compile_data', child_of=request.span):
            content = {}

            for proj in projects:
                if proj.address_id not in content:
                    content[proj.address_id] = {
                        'name': addresses[proj.address_id],
                        'data': {},
                    }
                # Add the Project to the Address it belongs to
                content[proj.address_id]['data'][proj.id] = {
                    'data': {},
                    'name': proj.name,
                    'region_id': proj.region_id,
                    'reseller_id': proj.reseller_id,
                }

                products = proj.get_billable_models()
                for product in products:
                    label = product.get_label()
                    product_data = {
                        'state': product.state,
                        'created': str(product.created),
                        'skus': product.get_sku_quantities(timestamp),
                    }
                    content[proj.address_id]['data'][proj.id]['data'][label] = product_data

        return Response({'content': content})


class CloudBillResource(APIView):
    """
    Given a project id, return the total number of SKUs for the Products in the Project
    """

    def get(self, request: Request, project_id: int) -> Response:
        """
        summary: Get the SKUs for the given Project
        description: |
            Retrieve the set of SKUs for all the products in the specified Project.

        parameters:
            - in: query
              name: timestamp
              schema:
                type: string
                format: date-time
              description: |
                An optional alternative timestamp to calculate hours off of, in ISO format.
                Defaults to the request time.

        path_params:
            project_id:
                description: The ID of the Project to calculate SKUs for
                type: integer

        responses:
            200:
                description: A set of SKUs for all the Products in the Project
                content:
                    application/json:
                        schema:
                            type: object
                            additionalProperties:
                                type: string
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        # Start by checking permissions
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, project_id)
            if err is not None:
                return err

        # Somehow ensure that the requested region is in fact a region
        with tracer.start_span('ensuring_valid_project', child_of=request.span):
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return Http404(error_code='iaas_cloud_bill_read_001')

        # Check that if a timestamp is sent, it is valid
        with tracer.start_span('check_sent_timestamp', child_of=request.span):
            stamp_str = request.GET.get('timestamp', '')
            if stamp_str is None or str(stamp_str).strip() == '':
                timestamp = datetime.utcnow()
            else:
                # Attempt to parse the sent string
                try:
                    timestamp = datetime.fromisoformat(stamp_str)
                except ValueError:
                    return Http400(error_code='iaas_cloud_bill_read_002')

        # Fetch all the necessary objects from the DB
        products = project.get_billable_models()

        # Loop through this list, calculate the skus for each
        # {label: {sku: amount}}
        skus: Dict[str, Dict[str, int]] = {}
        for product in products:
            skus[product.get_label()] = product.get_sku_quantities(timestamp)
        content = {'reseller_id': project.reseller_id, 'skus': skus}

        # Return the metrics data as requested
        return Response({'content': content})
