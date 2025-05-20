import re
from dataclasses import dataclass, field
from urllib.parse import ParseResult, urlparse

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

    def make_address(self, stash: Stash) -> Address:
        return S3Address.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return S3Address.from_string(address)

    def _save_stash(self, stash: Stash) -> Stash:
        self.s3_client.put_object(
            Bucket=stash.namespace,
            Key=f"{stash.name}.{stash.md5}",
            Body=stash.encoded,
        )
        return stash

    def load_stash(self, address: Address | str) -> Stash:
        address = self.parse_address(str(address))  # induce validation
        print(address)
        try:
            response = self.s3_client.get_object(
                Bucket=address.location,
                Key=address.path.strip("/"),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "NoSuchBucket"):  # type: ignore
                raise StashNotFound(str(address)) from e
            raise BackendRemoteError(self.name) from e

        raw = response.get("Body").read()
        data = msgpack.unpackb(raw)
        path_regex = r"(?P<name>.*)\.(?P<md5>[a-f0-9]{32})$"
        if not (match := re.match(path_regex, address.path)):
            raise ValueError(f"invalid address: {address}")
        grouped = match.groupdict()
        return Stash(
            name=grouped["name"].strip("/"),
            namespace=address.location,
            backend=self,
            data=data,
        )


@dataclass(frozen=True)
class S3Address(Address):
    scheme: str = "s3"

    @classmethod
    def from_string(cls, address: str) -> "S3Address":
        parsed: ParseResult = urlparse(address)
        if parsed.scheme != cls.scheme:
            raise ValueError(f"invalid s3 address: {address}")
        # TODO: validate parsed result, urlparse is lax.
        return cls(scheme=parsed.scheme, location=parsed.netloc, path=parsed.path)

    @classmethod
    def from_stash(cls, stash: Stash) -> "S3Address":
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=f"{stash.name}.{stash.md5}",
        )
