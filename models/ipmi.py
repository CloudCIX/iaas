# stdlib
import logging
from typing import Optional
# lib
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import CommitError, ConfigLoadError, ConnectError
# local
from .ip_address import IPAddress
from .pool_ip import PoolIP

__all__ = [
    'IPMI',
]


class IPMIManager(BaseManager):
    """
    Manager for IPMI that pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'customer_ip',
            'pool_ip',
            'customer_ip',
            'customer_ip__subnet',
            'customer_ip__subnet__allocation',
            'customer_ip__subnet__allocation__asn',
            'pool_ip',
        )


class IPMI(BaseModel):
    """

    """
    # Fields
    client_ip = models.GenericIPAddressField()
    customer_ip = models.ForeignKey(IPAddress, related_name='ipmi_logs', on_delete=models.PROTECT)
    modified_by = models.IntegerField(null=True)
    pool_ip = models.ForeignKey(PoolIP, related_name='logs', on_delete=models.PROTECT)
    removed = models.DateTimeField(null=True)

    # Use the new Manager
    objects = IPMIManager()

    class Meta:
        """
        Metadata about the model that Django can use.
        Metadata includes table names, indices, etc
        """
        db_table = 'ipmi'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            # Foreign Keys are automatically indexed by Django or Postgres, not sure which
            models.Index(fields=['id'], name='ipmi_id'),
            models.Index(fields=['client_ip'], name='ipmi_client_ip'),
            models.Index(fields=['created'], name='ipmi_created'),
            models.Index(fields=['deleted'], name='ipmi_deleted'),
            models.Index(fields=['modified_by'], name='ipmi_modified_by'),
            models.Index(fields=['removed'], name='ipmi_removed'),
            models.Index(fields=['updated'], name='ipmi_updated'),
        ]
        ordering = ['created']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the IPMIResource view for this IPMI record
        :return: A URL that corresponds to the views for this IPMI record
        """
        return reverse('ipmi_resource', kwargs={'pk': self.pk})

    @property
    def in_use(self) -> bool:
        """
        Determine whether or not this IPMI instance is currently being used
        """
        in_use = IPMI.objects.filter(pool_ip=self.pool_ip, removed__isnull=True).order_by('-created').first()
        return in_use is not None and in_use.pk == self.pk

    def deploy_to_router(self, device: Optional[Device]) -> Optional[str]:  # pragma: no cover
        """
        Add rules to the Firewall to setup the IPMI rules for the user.
        Return any error codes as necessary.
        """
        # If the device is None, we're in an environment where we are not going to actually set up IPMI rules.
        if device is None:
            return None

        # Create a logger for this method
        logger = logging.getLogger('iaas.ipmi.deploy_to_router')

        # Start attempting to connect and deploy the IPMI rules.
        try:
            logger.debug(f'Attempting to connect to router @ {device}', extra={'ipmi_id': self.pk})
            with device as dev:
                logger.debug(f'Successfully connected to router @ {device}', extra={'ipmi_id': self.pk})

                # Start by checking if the IPAddress in question has already been assigned
                logger.debug(
                    f'Determining if {self.customer_ip.address} already exists on router @ {device}',
                    extra={'ipmi_id': self.pk},
                )
                search_string = f'then static-nat prefix {self.customer_ip.address}/32'
                command_cli = f'show configuration | display set | match {self.customer_ip.address}'
                response = dev.cli(command_cli, warning=False)

                # Look for the appropriate line in the response
                found = False
                for line in response.split('\n'):
                    if line.endswith(search_string):
                        found = True
                        break
                if found:
                    logger.error(
                        f'Found {self.customer_ip.address} already existing on router @ {device}.',
                        extra={'ipmi_id': self.pk},
                    )
                    return 'iaas_ipmi_create_001'

                # Now that we know the address in question isn't already in the Router, let's put it there.
                # Set up our commands before opening the Config
                client_address = f'{self.client_ip}/32'
                pool_address = f'{self.pool_ip.ip_address}/32'
                cus_address = f'{self.customer_ip.address}/32'
                source_rule = f'OOB_Source_{self.pool_ip.pk}'
                access_rule = f'OOB_Access_{self.pool_ip.pk}'
                delete_command = f"""
                delete security nat static rule-set oob-inbound rule {access_rule}
                delete security address-book inet-public address {source_rule}
                """
                add_command = f"""
                set security nat static rule-set oob-inbound rule {access_rule} match source-address {client_address}
                set security nat static rule-set oob-inbound rule {access_rule} match destination-address {pool_address}
                set security nat static rule-set oob-inbound rule {access_rule} then static-nat prefix {cus_address}
                set security address-book inet-public address-set IPMI address {source_rule}
                set security address-book inet-public address {source_rule} {client_address}
                """

                # Open a Config instance and use it to start configuring the Router
                with Config(dev) as config:
                    # First, try to delete the previous address-book for this OOB Source
                    logger.debug(
                        f'Attempting to delete {source_rule} address-book from router @ {device}\n{delete_command}',
                        extra={'ipmi_id': self.pk},
                    )
                    try:
                        config.load(delete_command, format='set', ignore_warning=['statement not found'])
                    except ConfigLoadError:
                        logger.error(
                            f'An error occurred when attempting to load delete rules to router @ {device}\n'
                            f'{delete_command}',
                            exc_info=True,
                            extra={'ipmi_id': self.pk},
                        )
                        return 'iaas_ipmi_create_002'

                    # Now try to add the new rules for the IPMI setup
                    logger.debug(
                        f'Attempting to add new IPMI rules to router @ {device}\n{add_command}',
                        extra={'ipmi_id': self.pk},
                    )
                    try:
                        config.load(add_command, format='set')
                    except ConfigLoadError:
                        logger.error(
                            f'An error occurred when attempting to load add rules to router @ {device}\n'
                            f'{add_command}',
                            exc_info=True,
                            extra={'ipmi_id': self.pk},
                        )
                        try:
                            config.rollback()
                        except Exception:
                            pass
                        return 'iaas_ipmi_create_003'

                    # Finally, try to commit the changes
                    try:
                        config.commit()
                    except CommitError:
                        logger.error(
                            f'Unable to commit changes to router @ {device}',
                            exc_info=True,
                            extra={'ipmi_id': self.pk},
                        )
                        try:
                            config.rollback()
                        except Exception:
                            pass
                        return 'iaas_ipmi_create_004'
        except ConnectError:
            logger.error(
                f'Unable to connect to router @ {device}',
                exc_info=True,
                extra={'ipmi_id': self.pk},
            )
            return 'iaas_ipmi_create_005'
        except Exception:
            logger.error(
                f'An unexpected error occurred while attempting to deploy IPMI add rules to router @ {device}',
                exc_info=True,
                extra={'ipmi_id': self.pk},
            )
            return 'iaas_ipmi_create_006'
        logger.debug(f'Disconnected from router @ {device}', extra={'ipmi_id': self.pk})
        return None

    def remove_from_router(self, device: Optional[Device]) -> Optional[str]:  # pragma: no cover
        """
        Add rules to the Firewall to remove the IPMI rules for the user.
        Return any error codes as necessary.
        """
        # If the device is None, we're in an environment where we are not going to actually set up IPMI rules.
        if device is None:
            return None

        # Create a logger for this method
        logger = logging.getLogger('iaas.ipmi.remove_from_router')

        # Start attempting to connect and deploy the IPMI rules.
        try:
            logger.debug(f'Attempting to connect to router @ {device}', extra={'ipmi_id': self.pk})
            with device as dev:
                logger.debug(f'Successfully connected to router @ {device}', extra={'ipmi_id': self.pk})

                # Set up our commands before opening the Config
                client_address = f'{self.client_ip}/32'
                source_rule = f'OOB_Source_{self.pool_ip.pk}'
                access_rule = f'OOB_Access_{self.pool_ip.pk}'
                command = f"""
                delete security nat static rule-set oob-inbound rule {access_rule}
                delete security address-book inet-public address-set IPMI address {source_rule}
                delete security address-book inet-public address {source_rule} {client_address}
                """

                # Open a Config instance and use it to start configuring the Router
                with Config(dev) as config:
                    # Deploy the commands to delete the IPMI instance from the router.
                    logger.debug(
                        f'Attempting to remove IPMI rules from router @ {device}\n{command}',
                        extra={'ipmi_id': self.pk},
                    )
                    try:
                        config.load(command, format='set')
                    except ConfigLoadError:
                        logger.error(
                            f'An error occurred when attempting to load delete rules to router @ {device}\n'
                            f'{command}',
                            exc_info=True,
                            extra={'ipmi_id': self.pk},
                        )
                        try:
                            config.rollback()
                        except Exception:
                            pass
                        return 'iaas_ipmi_delete_002'

                    # Finally, try to commit the changes
                    try:
                        config.commit()
                    except CommitError:
                        logger.error(
                            f'Unable to commit changes to router @ {device}',
                            exc_info=True,
                            extra={'ipmi_id': self.pk},
                        )
                        try:
                            config.rollback()
                        except Exception:
                            pass
                        return 'iaas_ipmi_delete_003'
        except ConnectError:
            logger.error(
                f'Unable to connect to router @ {device}',
                exc_info=True,
                extra={'ipmi_id': self.pk},
            )
            return 'iaas_ipmi_delete_004'
        except Exception:
            logger.error(
                f'An unexpected error occurred while attempting to deploy IPMI delete rules to router @ {device}',
                exc_info=True,
                extra={'ipmi_id': self.pk},
            )
            return 'iaas_ipmi_delete_005'
        logger.debug(f'Disconnected from router @ {device}', extra={'ipmi_id': self.pk})
        return None
