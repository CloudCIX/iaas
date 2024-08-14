# libs
import serpy


__all__ = [
    'ProjectSerializer',
]


class ProjectSerializer(serpy.Serializer):
    """
    address_id:
        description: The ID of the Project address.
        type: integer
    closed:
        description: |
            A flag stating whether or not the Project is classified as closed.
            A Project is classified as closed when all the infrastructure in it is in a Closed state.
        type: boolean
    cloud_uri:
        description: The absolute URL of the Project for the Cloud service as opposed to the Project service
        type: string
    created:
        description: The date that the Project entry was created
        type: string
    grace_period:
        description: |
            Number of hours after a user scrub request before task is executed by robot.
            The default value is 168 (24 x 7).
        type: integer
    id:
        description: The ID of the Project.
        type: integer
    manager_id:
        description: The ID of the User that manages the Project
        type: integer
    min_state:
        description: The current minimum state of all infrastructure in the Project
        type: integer
    name:
        description: The name of the Project.
        type: string
    note:
        description: The note attached to the Project.
        type: string
    region_id:
        description: The region ID that the Project is in.
        type: integer
    reseller_id:
        description: The Address ID that will send the bill for the Project to the customer.
        type: integer
    shut_down:
        description: |
            A flag stating if the Project is classified as shut down.
            A Project is classified as shut down when all the infrastructure in it is in the Scrub set of states.
        type: boolean
    stable:
        description: |
            A flag stating if the Project is classified as stable.
            A Project is classified as stable when all the infrastructure in it is in a stable state e.g. Running,
            Quiesced or Scrubbed.
        type: boolean
    updated:
        description: The date that the Project entry was last updated
        type: string
    uri:
        description: The absolute URL of the Project that can be used to perform `Read`, `Update` and `Delete`
        type: string
    virtual_router_id:
        description: The ID of the Virtual Router for this Project.
        type: integer
    """
    address_id = serpy.Field()
    closed = serpy.Field()
    cloud_uri = serpy.Field(attr='get_cloud_url', call=True)
    created = serpy.Field(attr='created.isoformat', call=True)
    grace_period = serpy.Field()
    id = serpy.Field()
    manager_id = serpy.Field()
    min_state = serpy.Field()
    name = serpy.Field()
    note = serpy.Field(required=False)
    region_id = serpy.Field()
    reseller_id = serpy.Field()
    shut_down = serpy.Field()
    stable = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
    virtual_router_id = serpy.Field(attr='virtual_router.pk')
