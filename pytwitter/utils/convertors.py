"""
    Parameter convertors
"""
from pytwitter.error import PyTwitterError


def conv_type(field, _type, value):
    """
    Convert value to target type, and Checked.
    :param field: Name of the field you are checking.
    :param _type: Type that the value should be returned as.
    :param value: Value to convert to _type.
    :return:
    """
    try:
        return _type(value)
    except (ValueError, TypeError):
        raise PyTwitterError(f'"{field}" must be type {_type.__name__}')
