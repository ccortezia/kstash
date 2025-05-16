import base64
from dataclasses import dataclass

import msgpack

from .address import Address, InlineAddress, address_from_string
from .stash import ArgData, Stash


@dataclass(frozen=True)
class Backend:
    name: str

    def save_stash(self, name: str, data: ArgData, namespace: str = "default") -> Stash:
        stash = Stash(name=name, namespace=namespace, backend=self, data=data)
        return self._save_stash(stash)

    def _save_stash(self, stash: Stash) -> Stash:
        raise NotImplementedError

    def load_stash(self, address: Address) -> Stash:
        raise NotImplementedError

    def make_address(self, stash: Stash) -> Address:
        return Address(schema=self.name, namespace=stash.namespace, name=stash.name)


@dataclass(frozen=True)
class InlineBackend(Backend):
    name: str = "inline"

    def make_address(self, stash: Stash) -> Address:
        value = base64.b64encode(stash.encoded).decode("utf-8")
        return InlineAddress(
            schema=self.name,
            namespace=stash.namespace,
            name=stash.name,
            argdata=value,
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


@dataclass(frozen=True)
class MemBackend(Backend):
    name: str = "mem"

    def save_stash(self, name: str, data: ArgData, namespace: str = "default") -> Stash:
        raise NotImplementedError

    def load_stash(self, address: Address) -> Stash:
        raise NotImplementedError


def _inline_backend_for_value(value: ArgData) -> Backend | None:
    if not isinstance(value, (int, float, bool, str)):
        return None
    if isinstance(value, str) and len(value.encode("utf-8")) > 100:
        return None
    return InlineBackend()


def get_backend_from_value(value: ArgData) -> Backend:
    if inline_backend := _inline_backend_for_value(value):
        return inline_backend
    return MemBackend()


def get_backend_from_address(address: Address | str) -> Backend:
    if isinstance(address, str):
        address = address_from_string(address)
    if address.schema == "inline":
        return InlineBackend()
    elif address.schema == "mem":
        return MemBackend()
    raise RuntimeError(f"invalid address object: {address}")
