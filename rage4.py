"""
Methods to interact with Rage4.
Used to be a library but we're dropping that because it stopped some things from working
"""

# stdlib
import logging
import json
from typing import Any, Dict, Optional
# lib
import requests
from requests.exceptions import RequestException
# local
from iaas.models import AppSettings

__all__ = [
    'domain_create',
    'domain_delete',
    'domain_list',
    'domain_update',
    'record_create',
    'record_update',
    'record_delete',
    'reverse_domain_create',
]

# URLs
# Domain
DOMAIN_CREATE = 'https://secure.rage4.com/rapi/createregulardomain/'
DOMAIN_DELETE = 'https://secure.rage4.com/rapi/deletedomain/{}'
DOMAIN_LIST = 'https://secure.rage4.com/rapi/getdomains/'
DOMAIN_UPDATE = 'https://secure.rage4.com/rapi/updatedomain/{}'

# Reverse Domain Create
REVERSE_DOMAIN_CREATE = {
    4: 'https://secure.rage4.com/rapi/createreversedomain4/',
    6: 'https://secure.rage4.com/rapi/createreversedomain6/',
}

# Record
RECORD_CREATE = 'https://secure.rage4.com/rapi/createrecord/{}'
RECORD_DELETE = 'https://secure.rage4.com/rapi/deleterecord/{}'
RECORD_UPDATE = 'https://secure.rage4.com/rapi/updaterecord/{}'


def _call(
    url: str,
    params: Dict[str, Any],
    logger_name: str,
    email: bool,
) -> Optional[requests.Response]:  # pragma: no cover
    """
    This is the method that does the work, since the only differences in the methods are the URLs and logger names
    """
    logger = logging.getLogger(f'iaas.rage4.{logger_name}')  # pragma: no cover

    app_settings = AppSettings.objects.filter()[0]
    if app_settings.rage4_api_key is None or app_settings.rage4_email is None:
        logger.error('Error occurred when sending a request as Rage4 settings do not exist.')
        return None

    # Append rage4_email to params
    if email:
        params['email'] = app_settings.rage4_email

    try:
        return requests.get(
            url,
            params=params,
            auth=(app_settings.rage4_email, app_settings.rage4_api_key),
            timeout=5,
        )
    except RequestException:
        logger.error(
            f'Error occurred when sending a request with the following parameters;\n'
            f'{json.dumps(params, indent=2)}',
            exc_info=True,
        )
        return None


def domain_create(params: Dict[str, Any]) -> Optional[requests.Response]:  # pragma: no cover
    """
    Given data necessary to create a Domain in rage4, create it and return the response json.
    If the request fails for whatever reason, log some kind of message and return the output
    """
    email = True
    return _call(DOMAIN_CREATE, params, 'domain_create', email)


def domain_delete(pk: int) -> Optional[requests.Response]:  # pragma: no cover
    """
    Send a request to delete the domain with the specified ID
    """
    email = False
    return _call(DOMAIN_DELETE.format(pk), {}, 'domain_delete', email)


def domain_list() -> Optional[requests.Response]:  # pragma: no cover

    """
    Retrieve a list of domains in rage4.
    The only use for this is because we don't store PTR domains in the DB for some reason.
    """
    email = False
    return _call(DOMAIN_LIST, {}, 'domain_list', email)


def domain_update(pk: int, params: Dict[str, Any]) -> Optional[requests.Response]:  # pragma: no cover
    """
    Send a request to update the domain with the specified ID
    """
    email = True
    return _call(DOMAIN_UPDATE.format(pk), params, 'domain_update', email)


def record_create(domain_id: int, params: Dict[str, Any]) -> Optional[requests.Response]:  # pragma: no cover
    """
    Create a new record using the given details under the domain with the specified id
    """
    email = False
    return _call(RECORD_CREATE.format(domain_id), params, 'record_create', email)


def record_delete(pk: int) -> Optional[requests.Response]:  # pragma: no cover
    """
    Delete the specified record
    """
    email = False
    return _call(RECORD_DELETE.format(pk), {}, 'RECORD_DELETE', email)


def record_update(pk: int, params: Dict[str, Any]) -> Optional[requests.Response]:  # pragma: no cover
    """
    Update the specified record using the given details
    """
    email = False
    return _call(RECORD_UPDATE.format(pk), params, 'record_update', email)


def reverse_domain_create(version: int, params: Dict[str, Any]) -> Optional[requests.Response]:  # pragma: no cover
    """
    Create a reverse domain for the specified IP version
    """
    email = True
    return _call(REVERSE_DOMAIN_CREATE.get(version, ''), params, 'reverse_domain_create', email)
