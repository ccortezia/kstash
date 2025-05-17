from dataclasses import dataclass

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import StashNotFoundError
from .stash import Stash

MEM_BACKEND_STORE: dict[Address, Stash] = {}


@stash_backend("mem")
@dataclass(frozen=True)
class MemBackend(Backend):
    def _save_stash(self, stash: Stash) -> Stash:
        MEM_BACKEND_STORE[stash.address] = stash
        return stash

    def load_stash(self, address: Address) -> Stash:
        try:
            return MEM_BACKEND_STORE[address]
        except KeyError as error:
            raise StashNotFoundError(f"stash not found: {address}") from error
