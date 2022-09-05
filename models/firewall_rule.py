# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .virtual_router import VirtualRouter

__all__ = [
    'FirewallRule',
]


class FirewallRule(BaseModel):
    """
    A FirewallRule record represents a single User defined rule that is being implemented in the VirtualRouter for a
    Project.

    These records can be used to allow or block traffic with a given `source` and `destination`, on a given `port`
    using a given `protocol`.

    The special character '*' can be used in either source or destination to represent any public address.

    When `protocol` is 'any', 'port' is not required, which makes the rule act as an "Allow All" rule, which doesn't
    do any filtering.

    Also when `protocol` is 'icmp', 'port' is not required.

    Only one of `source` and `destination` can be a public networks, the other must be private, either relating to a
    cloud Subnet or IPAddress.
    """

    # Define the valid choices for protocol
    PROTOCOL_ANY = 'any'
    PROTOCOL_ICMP = 'icmp'
    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_CHOICES = (
        (PROTOCOL_ANY, PROTOCOL_ANY),
        (PROTOCOL_ICMP, PROTOCOL_ICMP),
        (PROTOCOL_TCP, PROTOCOL_TCP),
        (PROTOCOL_UDP, PROTOCOL_UDP),
    )

    # Fields
    allow = models.BooleanField()
    debug_logging = models.BooleanField(default=False)
    description = models.TextField()
    destination = models.TextField()
    order = models.IntegerField()
    pci_logging = models.BooleanField(default=False)
    port = models.CharField(max_length=11, null=True)
    protocol = models.CharField(max_length=4, choices=PROTOCOL_CHOICES)
    source = models.TextField()
    virtual_router = models.ForeignKey(VirtualRouter, related_name='firewall_rules', on_delete=models.CASCADE)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'firewall_rule'
        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='firewall_rule_id'),
            models.Index(fields=['deleted'], name='firewall_rule_deleted'),
            models.Index(fields=['order'], name='firewall_rule_order'),
        ]
