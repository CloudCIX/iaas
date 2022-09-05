# libs
import serpy


class AppSettingsSerializer(serpy.Serializer):
    """
    created:
        description: The date that the App Settings entry was created.
        type: string
    id:
        description: The ID of the App Settings record.
        type: integer
    ipmi_host:
        description: The IP address for the IPMI host.
        type: string
    ipmi_credentials:
        description: The credential for the IPMI host.
        type: string
    ipmi_username:
        description: The username for the IPMI host.
        type: string
    rage4_api_key:
        description: The API Key for Rage4 authentication to manage Public DNS records
        type: string
    rage4_email:
        description: The API Key for Rage4 authentication to manage Public DNS records
        type: string
    updated:
        description: The date that the App Settings entry was last updated.
        type: string
    uri:
        description: |
            The absolute URL of the App Settings record that can be used to perform `Read`, `Update` and `Delete`.
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    id = serpy.Field()
    ipmi_host = serpy.Field()
    ipmi_credentials = serpy.Field()
    ipmi_username = serpy.Field()
    rage4_api_key = serpy.Field()
    rage4_email = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
