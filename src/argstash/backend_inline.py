import base64
from dataclasses import dataclass

import msgpack

from .address import Address
from .backend_base import Backend, stash_backend
from .config import Config
from .exceptions import UnsupportedOperation
from .stash import ArgData, LinkedStash, Stash


@stash_backend("inline")
@dataclass(frozen=True)
class InlineBackend(Backend):
    def make_address(self, stash: Stash) -> Address:
        return InlineAddress.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return InlineAddress.from_string(address)

    def make_share_address(self, stash: Stash, ttl_sec: int = 10) -> str:
        raise UnsupportedOperation

    def _validate_input(self, data: ArgData, config: Config) -> bool:
        if not isinstance(data, (int, float, bool, str)):
            return False
        if isinstance(data, str) and len(data.encode("utf-8")) > config.max_inline_len:
            return False
        return True

    def _save_stash(self, stash: LinkedStash) -> LinkedStash:
        # Does nothing -- this backend does not persist data.
        return stash

    def load_stash(self, address: Address | str) -> LinkedStash:
        address = self.parse_address(str(address))  # induce validation
        raw = base64.b64decode(address.extra[0][1])
        data = msgpack.unpackb(raw)
        stash = Stash(
            name=address.path.strip("/"),
            namespace=address.location,
            data=data,
        )
        return stash.link(backend=self, address=address)


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
