# stdlib
# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse
# local

__all__ = [
    'AppSettings',
]


class AppSettings(BaseModel):
    """
    A App Settings object represents the required details for Rage4 to create public DNS records and Juniper Device for
    IPMI.
    """
    ipmi_credentials = models.CharField(max_length=128, null=True)
    ipmi_host = models.GenericIPAddressField(null=True)
    ipmi_username = models.CharField(max_length=250, null=True)
    rage4_api_key = models.TextField(null=True)
    rage4_email = models.CharField(max_length=255, null=True)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'app_settings'

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the AppSettingsResource view for this AppSettings record
        :return: A URL that corresponds to the views for this AppSettings record
        """
        return reverse('app_settings_resource', kwargs={'pk': self.pk})
