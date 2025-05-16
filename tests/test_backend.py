from typing import Any

import pytest

from argstash.address import address_from_string
from argstash.backend import get_backend_from_address, get_backend_from_value


@pytest.mark.parametrize(
    "value,backend_name",
    [
        pytest.param(1, "inline", id="int"),
        pytest.param("1", "inline", id="str_num"),
        pytest.param(1.2, "inline", id="float"),
        pytest.param(True, "inline", id="true"),
        pytest.param(False, "inline", id="false"),
        pytest.param(None, "mem", id="none"),
        pytest.param(b"1", "mem", id="small_bytes"),
        pytest.param(b"1234567890", "mem", id="large_bytes"),
        pytest.param({"a": 1}, "mem", id="dict"),
        pytest.param([1, 2, 3], "mem", id="list"),
        pytest.param("a" * 1000, "mem", id="long_str"),
    ],
)
def test_get_backend_from_value(value: Any, backend_name: str):
    backend = get_backend_from_value(value)
    assert backend.name == backend_name


@pytest.mark.parametrize(
    "address,backend_name",
    [
        pytest.param("mem://default/test", "mem", id="mem"),
        pytest.param("inline://default/test/cmVkICAxMQ==", "inline", id="inline"),
    ],
)
def test_get_backend_from_address(address: str, backend_name: str):
    backend = get_backend_from_address(address)
    assert backend.name == backend_name


def test_get_backend_from_unsupported_address_should_raise():
    address = address_from_string("inline://default/test/cmVkICAxMQ==")
    object.__setattr__(address, "schema", "invalid")
    with pytest.raises(RuntimeError):
        get_backend_from_address(address)
