import msgpack
import pytest
import responses
from kstash.backend_http import HttpBackend
from kstash.exceptions import BackendRemoteError, StashNotFound, UnsupportedOperation
from kstash.stash import Stash
from requests.exceptions import ConnectionError

SAMPLE_URL = "https://app.s3.amazonaws.com/x.34472d91b2f84052bf26d4eaa862ef86"

MALFORMED_URL = "https://app.s3.amazonaws.com/x.123"


def test_backend_http_cannot_save_stash():
    backend = HttpBackend()
    with pytest.raises(UnsupportedOperation):
        backend.save_stash("x", "config-data", namespace="app")


def test_backend_http_cannot_make_address():
    backend = HttpBackend()
    with pytest.raises(UnsupportedOperation):
        backend.make_address(Stash(name="x", data="config-data"))


def test_backend_http_cannot_share_stash():
    backend = HttpBackend()
    with pytest.raises(UnsupportedOperation):
        stash = Stash(name="x", data="config-data")
        backend.make_share_address(stash)


@responses.activate
def test_backend_http_load_stash_success():
    backend = HttpBackend()
    responses.add(responses.GET, SAMPLE_URL, body=msgpack.packb("123"))
    stash = backend.load_stash(SAMPLE_URL)
    assert stash.data == "123"


@responses.activate
def test_backend_http_load_when_invalid_address_should_raise():
    backend = HttpBackend()
    with pytest.raises(ValueError):
        backend.load_stash(MALFORMED_URL)


@responses.activate
def test_backend_http_load_stash_when_connection_error_should_raise():
    backend = HttpBackend()
    responses.add(responses.GET, SAMPLE_URL, body=ConnectionError("Mocked"))
    with pytest.raises(BackendRemoteError):
        backend.load_stash(SAMPLE_URL)


@responses.activate
def test_backend_http_load_stash_when_http_500_should_raise():
    backend = HttpBackend()
    responses.add(responses.GET, SAMPLE_URL, status=500)
    with pytest.raises(BackendRemoteError):
        backend.load_stash(SAMPLE_URL)


@responses.activate
def test_backend_http_load_stash_when_http_403_should_raise():
    backend = HttpBackend()
    responses.add(responses.GET, SAMPLE_URL, status=403)
    with pytest.raises(StashNotFound):
        backend.load_stash(SAMPLE_URL)


@responses.activate
def test_backend_http_load_stash_when_http_404_should_raise():
    backend = HttpBackend()
    responses.add(responses.GET, SAMPLE_URL, status=404)
    with pytest.raises(StashNotFound):
        backend.load_stash(SAMPLE_URL)
