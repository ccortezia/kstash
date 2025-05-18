from dataclasses import dataclass, field

import msgpack
from boto3.session import Session
from botocore.exceptions import ClientError
from types_boto3_s3 import S3Client

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import BackendRemoteError, StashNotFound
from .stash import Stash


@stash_backend("s3")
@dataclass(frozen=True)
class S3Backend(Backend):
    s3_client: S3Client = field(init=False)

    def __post_init__(self):
        session = Session()
        client: S3Client = session.client("s3")  # type: ignore
        object.__setattr__(self, "s3_client", client)

    def _save_stash(self, stash: Stash) -> Stash:
        self.s3_client.put_object(
            Bucket=stash.namespace,
            Key=stash.name,
            Body=stash.encoded,
        )
        return stash

    def load_stash(self, address: Address) -> Stash:
        try:
            response = self.s3_client.get_object(
                Bucket=address.namespace,
                Key=address.name,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "NoSuchBucket"):  # type: ignore
                raise StashNotFound(str(address)) from e
            raise BackendRemoteError(self.name) from e

        raw = response.get("Body").read()
        data = msgpack.unpackb(raw)
        return Stash(
            name=address.name,
            namespace=address.namespace,
            backend=self,
            data=data,
        )
