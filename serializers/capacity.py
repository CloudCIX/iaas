"""
Dummy Serializer to represent the output from the Capacity endpoint
"""
# lib
import serpy

__all__ = [
    'CapacitySerializer',
]


class CapacitySerializer(serpy.Serializer):
    """
    server_type:
        description: A dictionary mapping the server types to storage type dictionaries
        type: object
        properties:
            storage_type:
                description: A list of VM specs
                type: array
                items:
                    description: A dictionary of VM compute specs
                    type: object
                    properties:
                        ram:
                            description: How much RAM can be consumed
                            type: integer
                        storage:
                            description: |
                                How much storage can be consumed, the type being defined by the outer dictionary
                            type: integer
                        cpu:
                            description: How many CPU cores can be consumed
                            type: integer
    """
    server_type = serpy.Field()
