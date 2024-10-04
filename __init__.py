"""
The Infrastructure as a Service (IAAS) application is an API for the management of IP addresses and related entities and
for interacting with the Cloud platform through a RESTful API.

One major use case of the IAAS application is a method of interaction with the Rage4 DNS service for authorative DNS.
The IAAS application acts as middleware to the Rage4 DNS API.
One of the prime functions of the application is to control a CloudCIX Member's ability to create DNS records only for
IPAddresses that have already been asssigned to that Member.

The Services and Entities handled by the IAAS application are as follows;
- Allocations
    - An allocation is a range of IP addresses allocated to a customer for use in their system.
    - Allocations can be created by administrators of Members, within ASNs that have been assigned to them by CIX.
- Autonomous System Numbers (ASNs)
    - An ASN is issued to organisations by a Regional Internet Registry (RIR), such as RIPE.
    - Only CIX can modify ASN records, but these can be assigned to other Members who then have permission to view
      them
- Blacklist and Whitelist
    - CloudCIX operates and maintains a large blacklist and whitelist, managed and sourced by internal automated
      security systems.
    - The addresses in these lists can be viewed by any customer, who can then use them for their own benefits.
- Domains / Records / PTRRecords
    - These CloudCIX entities are what provide the middleware to the Rage4 DNS service.
    - Each Domain is associated with a Member, and each Record with a domain.
    - Each Member has full control over their own Domains and Records.
    - Deleting a Domain will remove all records associated with it as well.
- IPAddress
    - IPAddresses can be created and updated at will, provided they are in a Subnet that is owned by the requesting
      User's Address.
- IPValidator
    - This is a service that takes in an arbitrary number of address ranges and ip addresses, and validates them.
    - This service is available for everyone to use.
- Subnet
    - A Subnet is a network of IPAddresses, whose range falls under an Allocation that is assigned to a Address.
    - An Address has full control over the Subnets assigned to them.

Cloud Infrastructure cannot be deleted by customers via the usual means of a DELETE request.
Instead, cloud infrastructure must be updated with the state set to 8, at which point a grace period of 7 days will be
put in place for change of mind period.
At the end of the 7 day grace period, the Cloud platform will handle the deletion of the Project.
"""

__version__ = '3.3.0'
