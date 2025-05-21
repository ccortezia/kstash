import re
from dataclasses import dataclass, field

import msgpack
from boto3.session import Session
from botocore.exceptions import ClientError
from types_boto3_s3 import S3Client

from .address import Address
from .backend_base import Backend, stash_backend
from .backend_http import HttpAddress
from .exceptions import BackendRemoteError, StashNotFound
from .stash import SealedStash, Stash


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

    def _save_stash(self, stash: Stash) -> SealedStash:
        try:
            self.s3_client.put_object(
                Bucket=stash.namespace,
                Key=s3_key_from_stash(stash),
                Body=stash.encoded,
                IfNoneMatch="*",  # Prevents accidental stash overwriting.
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":  # type: ignore
                return self.load_stash(self.make_address(stash))
            raise BackendRemoteError(self.name) from e

        return stash.seal(backend=self, address=self.make_address(stash))

    def load_stash(self, address: Address | str) -> SealedStash:
        address = self.parse_address(str(address))  # induce validation

        # TODO: refactor and parse path natively during address construction
        path_regex = r"(?P<name>.*)\.(?P<md5>[a-f0-9]{32})$"
        if not (match := re.match(path_regex, address.path)):
            raise ValueError(f"invalid address: {address}")
        grouped = match.groupdict()
        stash_name = grouped["name"].strip("/")

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

        stash = Stash(name=stash_name, namespace=address.location, data=data)
        return stash.seal(backend=self, address=address)

    def make_share_address(self, stash: Stash, ttl_sec: int | None = None) -> Address:
        presigned_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": stash.namespace, "Key": s3_key_from_stash(stash)},
            ExpiresIn=ttl_sec or self.config.share_ttl_sec,
        )
        return HttpAddress.from_string(presigned_url)


@dataclass(frozen=True, kw_only=True)
class S3Address(Address):
    scheme: str = "s3"

    @classmethod
    def from_stash(cls, stash: Stash) -> "Address":
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=s3_key_from_stash(stash),
        )


def s3_key_from_stash(stash: Stash) -> str:
    return f"{stash.name}.{stash.md5}"
