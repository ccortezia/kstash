import msgpack
import pytest
from types_boto3_s3 import S3Client

from argstash.api import consume, create
from argstash.config import Config
from argstash.exceptions import StashNotFound
from argstash.stash import ArgData


@pytest.mark.parametrize(
    "arg_value",
    [
        pytest.param("red-red", id="alphanumeric"),
        pytest.param('"há não @!;"', id="text"),
        pytest.param(1, id="int"),
        pytest.param(1.0, id="float"),
        pytest.param(True, id="bool"),
    ],
)
def test_echo_inline_stash(arg_value: ArgData):
    stash = create("color", arg_value, namespace="app")
    assert stash.name == "color"
    assert stash.data == arg_value
    assert stash.encoded == msgpack.packb(arg_value)
    assert stash.backend.name == "inline"
    assert stash.namespace == "app"
    assert stash.name == "color"

    stash = consume(stash.address)
    assert stash.name == "color"
    assert stash.data == arg_value
    assert stash.backend.name == "inline"
    assert stash.namespace == "app"
    assert stash.encoded == msgpack.packb(arg_value)


def test_create_with_invalid_value_should_raise():
    class CustomClass:
        value = 10.09

    with pytest.raises(ValueError):
        create("test", CustomClass())  # type: ignore


@pytest.mark.parametrize(
    "arg_value",
    [
        pytest.param({"color": "red-red"}, id="dict"),
        pytest.param({"text": "há não @!;"}, id="dict_with_text"),
        pytest.param({"number": 1}, id="dict_with_int"),
        pytest.param({"float": 1.0}, id="dict_with_float"),
        pytest.param({"bool": True}, id="dict_with_bool"),
        pytest.param("c" * 101, id="large_string"),
    ],
)
def test_echo_memory_stash(arg_value: ArgData):
    config = Config(backends=["inline", "mem"])
    stash = create("mydatapoint", arg_value, namespace="app", config=config)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_value
    assert stash.encoded == msgpack.packb(arg_value)
    assert stash.backend.name == "mem"
    assert stash.namespace == "app"
    assert stash.name == "mydatapoint"

    stash = consume(stash.address)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_value
    assert stash.backend.name == "mem"
    assert stash.namespace == "app"
    assert stash.encoded == msgpack.packb(arg_value)


@pytest.mark.parametrize(
    "arg_value",
    [
        pytest.param({"color": "red-red"}, id="dict"),
        pytest.param({"text": "há não @!;"}, id="dict_with_text"),
        pytest.param({"number": 1}, id="dict_with_int"),
        pytest.param({"float": 1.0}, id="dict_with_float"),
        pytest.param({"bool": True}, id="dict_with_bool"),
        pytest.param("c" * 101, id="large_string"),
    ],
)
def test_echo_s3_stash(arg_value: ArgData, s3_setup: S3Client):
    config = Config(backends=["inline", "s3"])
    stash = create("mydatapoint", arg_value, namespace="app", config=config)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_value
    assert stash.encoded == msgpack.packb(arg_value)
    assert stash.backend.name == "s3"
    assert stash.namespace == "app"
    assert stash.name == "mydatapoint"

    stash = consume(stash.address)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_value
    assert stash.backend.name == "s3"
    assert stash.namespace == "app"
    assert stash.encoded == msgpack.packb(arg_value)


@pytest.mark.parametrize(
    "address",
    [
        pytest.param("mem://app/x.28a5e15a666b0cd1415490dcf6674255", id="mem"),
        pytest.param("s3://app/x.28a5e15a666b0cd1415490dcf6674255", id="s3"),
        pytest.param("s3://unknown/x.28a5e15a666b0cd1415490dcf6674255", id="s3"),
    ],
)
def test_consume_stash_not_found(address: str, s3_setup: S3Client):
    with pytest.raises(StashNotFound, match=address):
        consume(address)
