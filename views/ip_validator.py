"""
    Views for IPValidator
"""
# libs
from django.conf import settings
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
# local
from iaas.controllers import IPValidatorController

__all__ = [
    'IPValidator',
]


class IPValidator(APIView):
    """
    IPValidator
    """

    def get(self, request: Request) -> Response:
        """
        summary: Validate IP Addresses and IP Address ranges

        description: |
            The IP Validator will validate any sent IP Addresses or IP Address ranges.
            Along with any valid IP Address or range, a dictionary will be returned giving some extra details about it.

        parameters:
            - name: address_ranges
              description: |
                A string containing one or more gateway addresses for address ranges in CIDR notation, separated by
                commas.
                These address ranges will be validated to ensure they are correct, and will be returned along with
                some extra information about them that helps define the type of network they represent.
              schema:
                type: string
                nullable: true
              in: query
              required: false
            - name: ip_addresses
              description: |
                A string containing one or more IP addresses, separated by commas.
                These addresses will be validated to ensure they are in the correct format, and will be returned
                along with some extra information about them that helps understand the type of address they
                represent.

                Also, if `address_ranges` are also sent, then the addresses sent will also be double checked to
                ensure that they fit into one of the provided address ranges, and will be marked as such.
              schema:
                type: string
                nullable: true
              in: query
              required: false
        responses:
            200:
                description: A response containing the sent address ranges and IP addresses, which have been validated.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/IPValidator'
            400: {}
        """
        tracer = settings.TRACER

        if request.GET.get('address_ranges') is None and request.GET.get('ip_addresses') is None:
            return Http400(error_code='iaas_ip_validator_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = IPValidatorController(
                data=request.GET,
                request=request,
                span=span,
            )
            # This will never return False as we don't store errors in the controller errors dict in this view.
            controller.is_valid()
        return Response(controller.cleaned_data)
