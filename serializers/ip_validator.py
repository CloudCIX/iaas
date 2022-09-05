"""
Dummy Serializer to represent the output from the IPValidator endpoint
"""
# lib
import serpy

__all__ = [
    'IPValidatorSerializer',
]


class IPValidatorSerializer(serpy.Serializer):
    """
    address_ranges:
        description: A dictionary mapping the sent address ranges to the result information from the validator.
        type: object
        additionalProperties:
            type: object
            properties:
                error:
                    $ref: '#/components/schemas/Error'
                valid:
                    description: |
                        A flag stating whether or not the address range was found to be valid.
                        If valid is True, the errors array will always be empty.
                    type: boolean
                details:
                    description: |
                        A dictionary containing details about the validated address range.
                        Will be null if the address range is invalid.
                    nullable: true
                    type: object
                    properties:
                        ipv4:
                            description: |
                                A flag stating whether the address range is IPv4.
                                Will never be true if `ipv6` is true.
                            type: boolean
                        ipv6:
                            description: |
                                A flag stating whether the address range is IPv6.
                                Will never be true if `ipv4` is true.
                            type: boolean
                        network_address:
                            description: |
                                The network address for the range.
                                The network address is typically the first address in the range, and cannot be used.
                            type: string
                        netmask_address:
                            description: |
                                The netmask address for the range.
                                The netmask address is the subnet mask for the address range, in an ip address format.
                                For example, a `/24` IPv4 address range will have `255.255.255.0` as the netmask
                                address.
                            type: string
                        hostmask_address:
                            description: |
                                The hostmask address for the range.
                                The hostmask address is the opposite of the netmask address.
                                Where the netmask address shows the subnet mask in IP address form, the hostmask shows
                                the mask for the remainder of the address range.
                                For example, a `/24` IPv4 address range will have `0.0.0.255` as the hostmask address.
                            type: string
                        broadcast_address:
                            description: |
                                The broadcast address for the range.
                                The broadcast address is typically the last address in the range, and sending a message
                                to it will cause all hosts in the network to respond.
                                It cannot be assigned to a device in the network however.
                            type: string
                        cidr:
                            description: |
                                The Classless Inter-Domain Routing (CIDR) for the range.
                                CIDR is an IP addressing scheme that improves the allocation of IP addresses. It
                                replaces the old system based on classes A, B, and C. This scheme also helped greatly
                                extend the life of IPv4 as well as slow the growth of routing tables.
                            type: string
                        reference:
                            description: |
                                The reference for the address range.
                                If the address range is related to a special case RFC address range, this field will
                                contain the name of the RFC.
                                Otherwise, this field will just say 'IPv4' for IPv4 address ranges, and 'IPv6' for IPv6
                                ranges.
                            type: string
                        present_use:
                            description: |
                                The present use case for the address range.
                                Similarly to the `reference` field, if the address range is related to an RFC address
                                range, this field will contain a small description of the RFC.
                                Otherwise, this field will just say 'Public-Use Networks' for non RFC address ranges.
                            type: string
    ip_addresses:
        description: A dictionary mapping the sent ip addresses to the result information from the validator.
        type: object
        additionalProperties:
            type: object
            properties:
                error:
                    $ref: '#/components/schemas/Error'
                valid:
                    description: |
                        A flag stating whether or not the IP address was found to be valid.
                        If valid is True, the errors array will always be empty.
                    type: boolean
                details:
                    description: |
                        A dictionary containing details about the validated IP address.
                        Will be null if the IP address is invalid.
                    nullable: true
                    type: object
                    properties:
                        ipv4:
                            description: |
                                A flag stating whether the IP address is IPv4.
                                Will never be true if `ipv6` is true.
                            type: boolean
                        ipv6:
                            description: |
                                A flag stating whether the IP address is IPv6.
                                Will never be true if `ipv4` is true.
                            type: boolean
                        is_private:
                            description: A flag stating whether or not the given IP address is a private IP address.
                            type: boolean
                        is_reserved:
                            description: |
                                A flag stating whether or not the given IP address is a reserved IP address.
                                IP addresses are classified as reserved if they are special IP addresses reserved for
                                certain use cases.
                                An example of a reserved IP address is '0.0.0.0', as it is a special use case address
                                representing the current network.
                            type: boolean
                        is_loopback:
                            description: |
                                A flag stating whether or not the given IP address is a loopback IP address.
                                A loopback IP address is a special address that connects back to the same network card
                                as the one making the request.
                                '127.0.0.1' is the most common example of loopback IP addresses.
                            type: boolean
                        parent_network:
                            description: |
                                If both `address_ranges` and `ip_addresses` are sent, then the validator will, for each
                                IP address, search through the sent ranges for the address ranges that is its parent.
                                This address range will be sent back here.
                            type: string
                            nullable: true
    """
    address_ranges = serpy.Field()
    ip_addresses = serpy.Field()
