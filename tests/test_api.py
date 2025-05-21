import msgpack
import pytest
import responses
from kstash.api import create, retrieve
from kstash.config import Config
from kstash.exceptions import StashNotFound, UnsupportedBackend
from kstash.stash import ArgData
from types_boto3_s3 import S3Client


@pytest.mark.parametrize(
    "backend, arg_data",
    [
        pytest.param("inline", {"color": "red-red"}, id="inline.dict"),
        pytest.param("inline", {"text": "há não @!;"}, id="inline.dict_with_text"),
        pytest.param("inline", {"number": 1}, id="inline.dict_with_int"),
        pytest.param("inline", {"float": 1.0}, id="inline.dict_with_float"),
        pytest.param("inline", {"bool": True}, id="inline.dict_with_bool"),
        pytest.param("mem", {"color": "red-red"}, id="mem.dict"),
        pytest.param("mem", {"text": "há não @!;"}, id="mem.dict_with_text"),
        pytest.param("mem", {"number": 1}, id="mem.dict_with_int"),
        pytest.param("mem", {"float": 1.0}, id="mem.dict_with_float"),
        pytest.param("mem", {"bool": True}, id="mem.dict_with_bool"),
        pytest.param("mem", "c" * 101, id="mem.large_string"),
        pytest.param("s3", {"color": "red-red"}, id="s3.dict"),
        pytest.param("s3", {"text": "há não @!;"}, id="s3.dict_with_text"),
        pytest.param("s3", {"number": 1}, id="s3.dict_with_int"),
        pytest.param("s3", {"float": 1.0}, id="s3.dict_with_float"),
        pytest.param("s3", {"bool": True}, id="s3.dict_with_bool"),
        pytest.param("s3", "c" * 101, id="s3.large_string"),
    ],
)
def test_stash_creation_and_retrieval(
    backend: str,
    arg_data: ArgData,
    s3_setup: S3Client,
):
    config = Config(backends=[backend])
    stash = create("mydatapoint", arg_data, namespace="app", config=config)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_data
    assert stash.encoded == msgpack.packb(arg_data)
    assert stash.backend.name == backend
    assert stash.namespace == "app"
    assert stash.name == "mydatapoint"
    stash = retrieve(stash.address, config=config)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_data
    assert stash.backend.name == backend
    assert stash.namespace == "app"
    assert stash.encoded == msgpack.packb(arg_data)


@pytest.mark.parametrize(
    "backend, arg_data",
    [
        pytest.param("s3", {"color": "red-red"}, id="s3.dict"),
        pytest.param("s3", {"text": "há não @!;"}, id="s3.dict_with_text"),
        pytest.param("s3", {"number": 1}, id="s3.dict_with_int"),
        pytest.param("s3", {"float": 1.0}, id="s3.dict_with_float"),
        pytest.param("s3", {"bool": True}, id="s3.dict_with_bool"),
        pytest.param("s3", "c" * 101, id="s3.large_string"),
    ],
)
def test_stash_create_share_and_retrieve(
    backend: str,
    arg_data: ArgData,
    s3_setup: S3Client,
):
    config = Config(backends=[backend, "https"])
    stash = create("mydatapoint", arg_data, namespace="app", config=config)
    assert stash.name == "mydatapoint"
    assert stash.data == arg_data
    assert stash.encoded == msgpack.packb(arg_data)
    assert stash.backend.name == backend
    assert stash.namespace == "app"
    assert stash.name == "mydatapoint"

    shared_address = stash.share()
    assert shared_address.scheme == "https"
    assert shared_address.location == "app.s3.amazonaws.com"
    assert shared_address.path == f"/mydatapoint.{stash.md5}"

    shared_stash = retrieve(shared_address, config=config)
    assert shared_stash.namespace == "app"
    assert shared_stash.name == "mydatapoint"
    assert shared_stash.data == arg_data
    assert shared_stash.backend.name == "https"
    assert shared_stash.encoded == msgpack.packb(arg_data)


def test_create_skips_inline_for_large_data():
    config = Config(backends=["inline", "mem"])
    stash = create("mydatapoint", "c" * (config.max_inline_len + 1), config=config)
    assert stash.backend.name == "mem"


def test_create_with_no_available_backend_should_raise():
    config = Config(backends=["inline"])
    data_len = config.max_inline_len + 1
    with pytest.raises(UnsupportedBackend):
        create("test", "a" * data_len, config=config)


def test_create_with_invalid_value_should_raise():
    class CustomClass:
        value = 10.09

    with pytest.raises(ValueError):
        create("test", CustomClass())  # type: ignore


@pytest.mark.parametrize("backend", ["inline", "mem", "s3"])
@responses.activate
def test_create_stash_is_idempotent(backend: str, s3_setup: S3Client):
    config = Config(backends=[backend])
    stash1 = create("color", "red", namespace="app", config=config)
    stash2 = create("color", "red", namespace="app", config=config)
    assert stash1 == stash2


@pytest.mark.parametrize(
    "address",
    [
        pytest.param("mem://app/x.28a5e15a666b0cd1415490dcf6674255", id="mem"),
        pytest.param("mem://unknown/x.28a5e15a666b0cd1415490dcf6674255", id="mem"),
        pytest.param("s3://app/x.28a5e15a666b0cd1415490dcf6674255", id="s3"),
        pytest.param("s3://unknown/x.28a5e15a666b0cd1415490dcf6674255", id="s3"),
    ],
)
@responses.activate
def test_retrieve_stash_not_found(address: str, s3_setup: S3Client):
    config = Config(backends=["inline", "mem", "s3", "https"])
    with pytest.raises(StashNotFound, match=address):
        retrieve(address, config=config)


def test_retrieve_with_no_available_backend_should_raise():
    stash = create("test", "a", config=Config(backends=["inline"]))
    with pytest.raises(UnsupportedBackend):
        retrieve(stash.address, config=Config(backends=["s3"]))
