# libs
import serpy

__all__ = [
    'PolicyLogSerializer',
]


class PolicyLogSerializer(serpy.Serializer):
    """
    access:
        description: |
            A string representing what happened to the traffic.

            Currently possible values;
                - ALLOWED
                - BLOCKED
        type: string
    destination_address:
        description: The destination address of the traffic.
        type: string
    destination_port:
        description: The destination port of the traffic.
        type: integer
    service_name:
        description: |
            The name of the service as defined by Junos.

            Will be the string"None" if the traffic doesn't correspond with a known service.
        type: string
    source_address:
        description: The source address of the traffic.
        type: string
    source_port:
        description: The source port of the traffic.
        type: integer
    timestamp:
        description: The timestamp of the log message.
        type: string
    """
    access = serpy.Field()
    destination_address = serpy.Field()
    destination_port = serpy.Field()
    service_name = serpy.Field()
    source_address = serpy.Field()
    source_port = serpy.Field()
    timestamp = serpy.Field()
