from typing import Dict

import pytest

from argstash.address import address_from_string


@pytest.mark.parametrize(
    "addr_str,expected",
    [
        pytest.param(
            "inline://default/myvar/cmVkICAxMQ==",
            {"schema": "inline", "namespace": "default", "name": "myvar"},
            id="default-namespace-inline",
        ),
        pytest.param(
            "mem://custom/testvar",
            {"schema": "mem", "namespace": "custom", "name": "testvar"},
            id="custom-namespace-mem",
        ),
        pytest.param(
            "inline://my-namespace/my-variable/cmVkICAxMQ==",
            {"schema": "inline", "namespace": "my-namespace", "name": "my-variable"},
            id="hyphenated-namespace-and-name",
        ),
    ],
)
def test_valid_addresses(addr_str: str, expected: Dict[str, str]) -> None:
    addr = address_from_string(addr_str)
    assert addr.schema == expected["schema"]
    assert addr.namespace == expected["namespace"]
    assert addr.name == expected["name"]
    assert str(addr) == addr_str


@pytest.mark.parametrize(
    "invalid_addr",
    [
        pytest.param(
            "inline:/-invalid/myvar/cmVkICAxMQ==",
            id="bad-scheme-separator-1",
        ),
        pytest.param(
            "inline//-invalid/myvar",
            id="bad-scheme-separator-2",
        ),
        pytest.param(
            "/-invalid/myvar",
            id="missing-scheme",
        ),
        pytest.param(
            "unsupported://-invalid/myvar",
            id="invalid-scheme",
        ),
        pytest.param(
            "inline://-invalid/myvar/cmVkICAxMQ==",
            id="namespace-starts-with-hyphen",
        ),
        pytest.param(
            "inline://inv@lid/myvar/cmVkICAxMQ==",
            id="namespace-invalid-character",
        ),
        pytest.param(
            "inline://" + "a" * 41 + "/myvar/cmVkICAxMQ==",
            id="namespace-too-long",
        ),
        pytest.param(
            "inline://default/-myvar/cmVkICAxMQ==",
            id="name-starts-with-hyphen",
        ),
        pytest.param(
            "inline://default/my@var/cmVkICAxMQ==",
            id="name-invalid-character",
        ),
        pytest.param(
            "inline://default/" + "a" * 41 + "/cmVkICAxMQ==",
            id="name-too-long",
        ),
    ],
)
def test_invalid_address_format(invalid_addr: str) -> None:
    with pytest.raises(ValueError, match="invalid address:.*"):
        address_from_string(invalid_addr)


def test_string_representation():
    addr_str = "mem://test/var"
    addr = address_from_string(addr_str)
    assert str(addr) == addr_str
