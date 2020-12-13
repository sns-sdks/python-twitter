"""
    Parameters validators
"""
from typing import List, Tuple, Union

from pytwitter.error import PyTwitterError


def enf_comma_separated(name: str, value: Union[str, List, Tuple]):
    """
    Check to see if field's value type belong to correct type.
    If accepted, return formatted value, otherwise, raise a Error.
    :param name: The parameter field name.
    :param value: Value for provide.
    :return: Formatted comma-separated list
    """

    if not value:
        return None

    if isinstance(value, str):
        return value
    elif isinstance(value, (List, Tuple)):
        return ",".join(value)
    else:
        raise PyTwitterError(
            f"Parameter {name} must be comma-separated str, list or tuple"
        )
