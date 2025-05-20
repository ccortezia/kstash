import pytest
import responses
from fdstash.backend_http import HttpBackend
from fdstash.exceptions import BackendRemoteError, StashNotFound, UnsupportedOperation
from fdstash.stash import Stash
from requests.exceptions import ConnectionError


def test_backend_http_cannot_save_stash():
    backend = HttpBackend()
    with pytest.raises(UnsupportedOperation):
        backend.save_stash("x", "config-data", namespace="app")


def test_backend_http_cannot_share_stash():
    backend = HttpBackend()
    with pytest.raises(UnsupportedOperation):
        stash = Stash(name="x", data="config-data")
        backend.make_share_address(stash)


@responses.activate
def test_backend_http_when_connection_error_should_raise():
    backend = HttpBackend()
    responses.add(
        responses.GET,
        "https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66",
        body=ConnectionError("Mocked"),
    )
    with pytest.raises(BackendRemoteError):
        backend.load_stash("https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66")


@responses.activate
def test_backend_http_when_http_500_should_raise():
    backend = HttpBackend()
    responses.add(
        responses.GET,
        "https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66",
        status=500,
    )
    with pytest.raises(BackendRemoteError):
        backend.load_stash("https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66")


@responses.activate
def test_backend_http_when_http_403_should_raise():
    backend = HttpBackend()
    responses.add(
        responses.GET,
        "https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66",
        status=403,
    )
    with pytest.raises(StashNotFound):
        backend.load_stash("https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66")


@responses.activate
def test_backend_http_when_http_404_should_raise():
    backend = HttpBackend()
    responses.add(
        responses.GET,
        "https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66",
        status=404,
    )
    with pytest.raises(StashNotFound):
        backend.load_stash("https://app.s3.amazonaws.com/x.28a5e15a666b0cd1415490dcf66")
