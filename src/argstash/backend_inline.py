import base64
from dataclasses import dataclass
from urllib.parse import ParseResult, parse_qsl, urlparse

import msgpack

from .address import Address
from .backend_base import Backend, stash_backend
from .config import Config
from .stash import ArgData, Stash


@stash_backend("inline")
@dataclass(frozen=True)
class InlineBackend(Backend):
    def accepts(self, value: ArgData, config: Config) -> bool:
        # TODO: postpone validation to stash construction. use a catch pattern.
        if not isinstance(value, (int, float, bool, str)):
            return False
        if (
            isinstance(value, str)
            and len(value.encode("utf-8")) > config.max_inline_len
        ):
            return False
        return True

    def make_address(self, stash: Stash) -> Address:
        return InlineAddress.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return InlineAddress.from_string(address)

    def _save_stash(self, stash: Stash) -> Stash:
        # Does nothing -- this backend does not persist data.
        return stash

    def load_stash(self, address: Address | str) -> Stash:
        address = self.parse_address(str(address))  # induce validation
        raw = base64.b64decode(address.extra[0][1])
        data = msgpack.unpackb(raw)
        return Stash(
            name=address.path.strip("/"),
            namespace=address.location,
            backend=self,
            data=data,
        )


class InlineAddress(Address):
    scheme: str = "inline"

    @classmethod
    def from_string(cls, address: str) -> "InlineAddress":
        parsed: ParseResult = urlparse(address)
        # TODO: validate parsed result, urlparse is lax.
        if parsed.scheme != cls.scheme:
            raise ValueError(f"invalid inline address: {address}")
        return cls(
            scheme=parsed.scheme,
            location=parsed.netloc,
            path=parsed.path,
            extra=parse_qsl(parsed.query),
        )

    @classmethod
    def from_stash(cls, stash: Stash) -> "InlineAddress":
        data = base64.b64encode(stash.encoded).decode("utf-8")
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=stash.name,
            extra=[("data", data)],
        )
