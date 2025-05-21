import base64
from dataclasses import dataclass

import msgpack

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import UnsupportedOperation
from .stash import SealedStash, Stash


@stash_backend("inline")
@dataclass(frozen=True, kw_only=True)
class InlineBackend(Backend):
    def make_address(self, stash: Stash) -> Address:
        return InlineAddress.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return InlineAddress.from_string(address)

    def make_share_address(self, stash: Stash, ttl_sec: int | None = None) -> Address:
        raise UnsupportedOperation

    def _save_stash(self, stash: Stash) -> SealedStash:
        address = self.make_address(stash)
        if len(address.extra[0][1]) > self.config.max_inline_len:
            raise UnsupportedOperation("data: too large to inline")
        return stash.seal(backend=self, address=address)

    def load_stash(self, address: Address | str) -> SealedStash:
        address = self.parse_address(str(address))
        raw = base64.b64decode(address.extra[0][1])
        data = msgpack.unpackb(raw)
        return SealedStash(
            name=address.path.strip("/"),
            namespace=address.location,
            data=data,
            backend=self,
            address=address,
        )


@dataclass(frozen=True, kw_only=True)
class InlineAddress(Address):
    scheme: str = "inline"

    @classmethod
    def from_stash(cls, stash: Stash) -> "InlineAddress":
        data = base64.b64encode(stash.encoded).decode("utf-8")
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=stash.name,
            extra=[("data", data)],
        )
