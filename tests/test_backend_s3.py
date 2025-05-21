import pytest
from botocore.exceptions import ClientError
from kstash.api import Config, create
from kstash.backend_s3 import S3Backend
from kstash.exceptions import BackendRemoteError
from pytest import MonkeyPatch
from types_boto3_s3 import S3Client


def test_s3_backend_save_stash_remote_error(
    s3_setup: S3Client, monkeypatch: MonkeyPatch
):
    backend = S3Backend()
    monkeypatch.setattr(backend.s3_client, "put_object", mock_put_object)  # type: ignore
    with pytest.raises(BackendRemoteError):
        backend.save_stash("x", "config-data", namespace="app")


def test_s3_backend_load_stash_remote_error(
    s3_setup: S3Client, monkeypatch: MonkeyPatch
):
    backend = S3Backend()
    stash = backend.save_stash("x", "config-data", namespace="app")
    monkeypatch.setattr(backend.s3_client, "get_object", mock_get_object)  # type: ignore
    with pytest.raises(BackendRemoteError):
        backend.load_stash(stash.address)


def test_s3_backend_load_stash_bad_path(s3_setup: S3Client):
    backend = S3Backend()
    with pytest.raises(ValueError):
        backend.load_stash("s3://app/x.28a5e15a666b0cd1415490dcf66")


def test_stash_share(s3_setup: S3Client):
    config = Config(backends=["s3", "https"])
    stash = create("mydatapoint", {"color": "red"}, namespace="app", config=config)
    share_address = stash.share()
    assert str(share_address).startswith("https://")


def mock_get_object(*args: object, **kwargs: object) -> None:
    raise ClientError(
        error_response={"Error": {"Code": "InternalError", "Message": "Mocked"}},
        operation_name="GetObject",
    )


def mock_put_object(*args: object, **kwargs: object) -> None:
    raise ClientError(
        error_response={"Error": {"Code": "InternalError", "Message": "Mocked"}},
        operation_name="PutObject",
    )
