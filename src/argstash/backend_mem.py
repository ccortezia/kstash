from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import StashNotFound
from .stash import Stash

MEM_BACKEND_STORE: dict[str, Stash] = {}


@stash_backend("mem")
@dataclass(frozen=True)
class MemBackend(Backend):
    def _save_stash(self, stash: Stash) -> Stash:
        MEM_BACKEND_STORE[str(stash.address)] = stash
        return stash

    def make_address(self, stash: Stash) -> Address:
        return MemAddress.from_stash(stash)

    def parse_address(self, address: str) -> Address:
        return MemAddress.from_string(address)

    def load_stash(self, address: Address | str) -> Stash:
        address = self.parse_address(str(address))
        try:
            return MEM_BACKEND_STORE[str(address)]
        except KeyError as error:
            raise StashNotFound(f"stash not found: {address}") from error


@dataclass(frozen=True)
class MemAddress(Address):
    scheme: str = "mem"

    @classmethod
    def from_string(cls, address: str) -> "MemAddress":
        parsed: ParseResult = urlparse(address)
        if parsed.scheme != cls.scheme:
            raise ValueError(f"invalid mem address: {address}")
        return cls(scheme=parsed.scheme, location=parsed.netloc, path=parsed.path)

    @classmethod
    def from_stash(cls, stash: Stash) -> "MemAddress":
        return cls(
            scheme=cls.scheme,
            location=stash.namespace,
            path=stash.name,
        )
