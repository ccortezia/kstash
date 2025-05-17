import base64
from dataclasses import dataclass

import msgpack

from .address import Address, InlineAddress
from .backend_base import Backend, stash_backend
from .config import Config
from .stash import ArgData, Stash


@stash_backend("inline")
@dataclass(frozen=True)
class InlineBackend(Backend):
    def accepts(self, value: ArgData, config: Config) -> bool:
        if not isinstance(value, (int, float, bool, str)):
            return False
        if (
            isinstance(value, str)
            and len(value.encode("utf-8")) > config.max_inline_len
        ):
            return False
        return True

    def make_address(self, stash: Stash) -> Address:
        value = base64.b64encode(stash.encoded).decode("utf-8")
        return InlineAddress(
            schema=self.name,
            namespace=stash.namespace,
            name=stash.name,
            argdata=value,
            md5=stash.md5,
        )

    def _save_stash(self, stash: Stash) -> Stash:
        # Does nothing -- this backend does not persist data.
        return stash

    def load_stash(self, address: Address) -> Stash:
        if not isinstance(address, InlineAddress):
            raise ValueError(f"invalid address: {address}")
        raw = base64.b64decode(address.argdata)
        data = msgpack.unpackb(raw)
        return Stash(
            name=address.name,
            namespace=address.namespace,
            backend=self,
            data=data,
        )
