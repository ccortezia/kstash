from typing import Dict

import pytest

from argstash.address import address_from_string


@pytest.mark.parametrize(
    "addr_str,expected",
    [
        pytest.param(
            "inline://default/myvar/sGFkanVzdGluZz1jb2xvcjs=",
            {"schema": "inline", "namespace": "default", "name": "myvar"},
            id="inline-simple-segments",
        ),
        pytest.param(
            "inline://my-namespace/my-variable/sGFkanVzdGluZz1jb2xvcjs=",
            {"schema": "inline", "namespace": "my-namespace", "name": "my-variable"},
            id="inline-hyphenated-segments",
        ),
        pytest.param(
            "mem://custom/testvar.28a5e15a666b0cd1415490dcf6674255",
            {
                "schema": "mem",
                "namespace": "custom",
                "name": "testvar",
                "md5": "28a5e15a666b0cd1415490dcf6674255",
            },
            id="mem-simple-segments",
        ),
        pytest.param(
            "mem://my-namespace/my-variable.28a5e15a666b0cd1415490dcf6674255",
            {
                "schema": "mem",
                "namespace": "my-namespace",
                "name": "my-variable",
                "md5": "28a5e15a666b0cd1415490dcf6674255",
            },
            id="mem-simple-segments",
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
            "inline:/-invalid/myvar/sGFkanVzdGluZz1jb2xvcjs=",
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
            "inline://-invalid/myvar/sGFkanVzdGluZz1jb2xvcjs=",
            id="namespace-starts-with-hyphen",
        ),
        pytest.param(
            "inline://inv@lid/myvar/sGFkanVzdGluZz1jb2xvcjs=",
            id="namespace-invalid-character",
        ),
        pytest.param(
            "inline://" + "a" * 41 + "/myvar/sGFkanVzdGluZz1jb2xvcjs=",
            id="namespace-too-long",
        ),
        pytest.param(
            "inline://default/-myvar/sGFkanVzdGluZz1jb2xvcjs=",
            id="name-starts-with-hyphen",
        ),
        pytest.param(
            "inline://default/my@var/sGFkanVzdGluZz1jb2xvcjs=",
            id="name-invalid-character",
        ),
        pytest.param(
            "inline://default/" + "a" * 41 + "/sGFkanVzdGluZz1jb2xvcjs=",
            id="name-too-long",
        ),
    ],
)
def test_invalid_address_format(invalid_addr: str) -> None:
    with pytest.raises(ValueError, match="invalid address:.*"):
        address_from_string(invalid_addr)


def test_string_representation():
    addr_str = "mem://test/var.28a5e15a666b0cd1415490dcf6674255"
    addr = address_from_string(addr_str)
    assert str(addr) == addr_str
