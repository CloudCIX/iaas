"""
Utility file for extra validation methods
"""
from typing import Optional

__all__ = [
    'validate_domain_name',
]

LENGTH = 240
SEGMENT_LENGTH = 63


def validate_domain_name(domain_name: str, length_code: str, segment_length_code: str) -> Optional[str]:
    """
    Validate a given domain name using both the total length of it and the length of the segments.
    If the total length is more than 240, return the `length_code` parameter.
    If the length of one of the segments is too long, return the `segment_length_code`.
    If all is valid, return None.
    """
    if len(domain_name) > LENGTH:
        return length_code

    # Ensure that each part of the name, when split on '.', is not longer than 63 characters.
    if any(len(seg) > SEGMENT_LENGTH for seg in domain_name.split('.')):
        return segment_length_code

    return None
