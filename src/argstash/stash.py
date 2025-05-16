import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import msgpack

from .address import Address

if TYPE_CHECKING:
    from .backend import Backend

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
    address: Address = field(init=False)
    backend: "Backend"
    encoded: bytes = field(init=False)
    md5: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "encoded", self._encode(self.data))
        object.__setattr__(self, "md5", hashlib.md5(self.encoded).hexdigest())
        object.__setattr__(self, "address", self.backend.make_address(self))

    def _encode(self, data: ArgData) -> bytes:
        try:
            return msgpack.packb(data)
        except Exception as error:
            raise ValueError(f"invalid data: {data}") from error
