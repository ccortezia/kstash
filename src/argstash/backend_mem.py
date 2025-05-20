from dataclasses import dataclass

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import StashNotFound, UnsupportedOperation
from .stash import LinkedStash, Stash

MEM_BACKEND_STORE: dict[str, LinkedStash] = {}


@stash_backend("mem")
@dataclass(frozen=True)
class MemBackend(Backend):
    def _save_stash(self, stash: LinkedStash) -> LinkedStash:
        MEM_BACKEND_STORE[str(stash.address)] = stash
        return stash

    def make_address(self, stash: Stash) -> Address:
        return MemAddress.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return MemAddress.from_string(address)

    def make_share_address(self, stash: Stash, ttl_sec: int = 10) -> str:
        raise UnsupportedOperation

    def load_stash(self, address: Address | str) -> LinkedStash:
        address = self.parse_address(str(address))
        try:
            return MEM_BACKEND_STORE[str(address)]
        except KeyError as error:
            raise StashNotFound(f"stash not found: {address}") from error


@dataclass(frozen=True, kw_only=True)
class MemAddress(Address):
    scheme: str = "mem"

    @classmethod
    def from_stash(cls, stash: Stash) -> "Address":
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=stash.name,
        )
