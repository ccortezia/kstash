import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import msgpack

from .address import Address

if TYPE_CHECKING:
    from .backend_base import Backend

type JSONData = (
    str | int | float | bool | None | list["JSONData"] | dict[str, "JSONData"]
)
type BinData = bytes | bytearray
type ArgData = JSONData | BinData


@dataclass(kw_only=True, frozen=True)
class Stash:
    namespace: str = "default"
    name: str
    data: ArgData
    encoded: bytes = field(init=False)
    md5: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "encoded", self._encode(self.data))
        object.__setattr__(self, "md5", hashlib.md5(self.encoded).hexdigest())

    def _encode(self, data: ArgData) -> bytes:
        try:
            return msgpack.packb(data)
        except Exception as error:
            raise ValueError(f"invalid data: {data}") from error

    def __repr__(self) -> str:
        return f"Stash(name={self.name}, namespace={self.namespace})"

    def link(self, backend: "Backend", address: Address | None = None):
        return LinkedStash(
            namespace=self.namespace,
            name=self.name,
            data=self.data,
            backend=backend,
            address=address or backend.make_address(self),
        )


@dataclass(kw_only=True, frozen=True)
class LinkedStash(Stash):
    backend: "Backend"
    address: Address

    def __repr__(self) -> str:
        return f"Stash(name={self.name}, namespace={self.namespace}, address={self.address})"
