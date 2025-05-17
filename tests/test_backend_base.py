from typing import Any

import pytest

from argstash.address import address_from_string
from argstash.backend import get_backend_from_address, get_backend_from_value
from argstash.backend_inline import InlineBackend
from argstash.config import CONFIG, Config
from argstash.exceptions import UnknownBackendError


@pytest.mark.parametrize(
    "value,backend_name,config",
    [
        pytest.param(1, "inline", Config(), id="int"),
        pytest.param("1", "inline", Config(), id="str_num"),
        pytest.param(1.2, "inline", Config(), id="float"),
        pytest.param(True, "inline", Config(), id="true"),
        pytest.param(False, "inline", Config(), id="false"),
        pytest.param(None, "mem", Config(backends=["inline", "mem"]), id="none"),
        pytest.param(b"1", "mem", Config(backends=["inline", "mem"]), id="bytes"),
        pytest.param({"a": 1}, "mem", Config(backends=["inline", "mem"]), id="dict"),
        pytest.param([1, 2, 3], "mem", Config(backends=["inline", "mem"]), id="list"),
        pytest.param("a" * 1000, "mem", Config(backends=["inline", "mem"]), id="long"),
        pytest.param(None, "s3", Config(backends=["inline", "s3"]), id="none"),
        pytest.param(b"1", "s3", Config(backends=["inline", "s3"]), id="bytes"),
        pytest.param({"a": 1}, "s3", Config(backends=["inline", "s3"]), id="dict"),
        pytest.param([1, 2, 3], "s3", Config(backends=["inline", "s3"]), id="list"),
        pytest.param("a" * 1000, "s3", Config(backends=["inline", "s3"]), id="long"),
    ],
)
def test_get_backend_from_value(value: Any, backend_name: str, config: Config):
    backend = get_backend_from_value(value, config)
    assert backend.name == backend_name


@pytest.mark.parametrize(
    "address,backend_name",
    [
        pytest.param("inline://ns/x/cmVkICAxMQ==", "inline", id="inline"),
        pytest.param("mem://ns/x.28a5e15a666b0cd1415490dcf6674255", "mem", id="mem"),
        pytest.param("s3://ns/x.28a5e15a666b0cd1415490dcf6674255", "s3", id="s3"),
    ],
)
def test_get_backend_from_address(address: str, backend_name: str):
    backend = get_backend_from_address(address, CONFIG)
    assert backend.name == backend_name


def test_get_backend_from_address_unsupported_schema_should_raise():
    address = address_from_string("inline://default/test/cmVkICAxMQ==")
    object.__setattr__(address, "schema", "invalid")
    with pytest.raises(UnknownBackendError):
        get_backend_from_address(address, CONFIG)


def test_get_backend_from_value_unsupported_backend_should_raise():
    with pytest.raises(UnknownBackendError):
        get_backend_from_value({"a": 1}, Config(backends=["inline"]))


def test_inline_backend_load_stash_with_incompatible_address_should_raise():
    address = address_from_string("mem://default/test.28a5e15a666b0cd1415490dcf6674255")
    with pytest.raises(ValueError):
        InlineBackend().load_stash(address)
