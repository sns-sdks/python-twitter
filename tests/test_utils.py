"""
    Utils tests
"""
import pytest

from pytwitter.error import PyTwitterError
from pytwitter.utils.validators import enf_comma_separated
from pytwitter.utils.convertors import conv_type


def test_comma_separated():
    value_is_none = enf_comma_separated(name="none", value="")
    assert value_is_none is None

    value_is_str = enf_comma_separated(name="str", value="id1,id2")
    assert value_is_str == "id1,id2"

    value_is_list = enf_comma_separated(name="array", value=["id1", "id2"])
    assert value_is_list == "id1,id2"

    value_is_tuple = enf_comma_separated(name="tuple", value=("id1", "id2"))
    assert value_is_tuple == "id1,id2"

    with pytest.raises(PyTwitterError) as ex:
        enf_comma_separated(name="other", value={1, 2, 3})  # noqa
    assert "comma-separated" in ex.value.message  # noqa


def test_conv_type():
    with pytest.raises(PyTwitterError) as e:
        conv_type("limit", int, None)

    assert "limit" in e.value.message
