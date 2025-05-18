import boto3
import pytest
from moto import mock_aws
from types_boto3_s3 import S3Client


@pytest.fixture(scope="function")
def s3():
    with mock_aws():
        s3_client: S3Client = boto3.client("s3")  # type: ignore
        yield s3_client


@pytest.fixture(scope="function")
def s3_setup(s3: S3Client):
    s3.create_bucket(Bucket="app")
    yield s3
