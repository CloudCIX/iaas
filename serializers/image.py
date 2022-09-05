# libs
import serpy

__all__ = [
    'ImageSerializer',
]


class ImageSerializer(serpy.Serializer):
    """
    answer_file_name:
        description: |
            The name of the answer file is an XML-based file that contains setting definitions and values to use during
            the VM build process.
        type: string
    cloud_init:
        description: Boolean representing if this image supports Cloud Init.
        type: boolean
    created:
        description: The date that the Image entry was created
        type: string
    display_name:
        description: The name of the Image.
        type: string
    filename:
        description: The name of the file containing the Image.
        type: string
    id:
        description: The ID of the Image.
        type: integer
    multiple_ips:
        description: Boolean representing if multiple ips can be configured on a VM using this image.
        type: boolean
    os_variant:
        description: Is a unique word to define each Image on a KVM host.
        type: string
    regions:
        description: List of regions the Image is available in.
        type: array
        items:
            type: integer
    updated:
        description: The date that the Image entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the Image record that can be used to perform `Read`, `Update` and `Delete`
        type: string
    """

    answer_file_name = serpy.Field()
    cloud_init = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    display_name = serpy.Field()
    filename = serpy.Field()
    id = serpy.Field()
    multiple_ips = serpy.Field()
    os_variant = serpy.Field()
    regions = serpy.Field(attr='get_regions', call=True)
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
