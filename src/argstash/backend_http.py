from dataclasses import dataclass

import msgpack
import requests

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import BackendRemoteError, StashNotFound, UnsupportedOperation
from .stash import LinkedStash, Stash


@stash_backend("https")
@dataclass(frozen=True)
class HttpBackend(Backend):
    def parse_address(self, address: str) -> Address:
        return HttpAddress.from_string(address)

    def make_address(self, stash: Stash) -> Address:
        raise UnsupportedOperation

    def make_share_address(self, stash: Stash, ttl_sec: int = 10) -> str:
        raise UnsupportedOperation

    def load_stash(self, address: Address | str) -> LinkedStash:
        address = self.parse_address(str(address))

        try:
            response = requests.get(str(address))
        except requests.RequestException as error:
            raise BackendRemoteError(self.name) from error

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            if error.response.status_code in (403, 404):
                raise StashNotFound(f"stash not found: {address}") from error
            raise BackendRemoteError(self.name) from error

        data = msgpack.unpackb(response.content)

        stash = Stash(
            name=address.path.strip("/"),
            namespace=address.location,
            data=data,
        )

        return stash.link(backend=self, address=address)


@dataclass(frozen=True, kw_only=True)
class HttpAddress(Address):
    scheme: str = "https"
