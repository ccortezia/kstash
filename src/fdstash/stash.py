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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stash):
            return False
        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.md5 == other.md5
        )

    def seal(self, backend: "Backend", address: Address | None = None) -> "SealedStash":
        return SealedStash(
            namespace=self.namespace,
            name=self.name,
            data=self.data,
            backend=backend,
            address=address or backend.make_address(self),
        )


@dataclass(kw_only=True, frozen=True)
class SealedStash(Stash):
    backend: "Backend"
    address: Address

    def __repr__(self) -> str:
        return f"Stash(name={self.name}, namespace={self.namespace}, address={self.address})"

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def share(self, ttl_sec: int | None = None) -> "Address":
        return self.backend.make_share_address(self, ttl_sec)
