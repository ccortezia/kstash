import re
from dataclasses import dataclass

import msgpack
import requests

from .address import Address
from .backend_base import Backend, stash_backend
from .exceptions import BackendRemoteError, StashNotFound, UnsupportedOperation
from .stash import SealedStash, Stash


@stash_backend("https")
@dataclass(frozen=True)
class HttpBackend(Backend):
    def parse_address(self, address: str) -> Address:
        return HttpAddress.from_string(address)

    def make_address(self, stash: Stash) -> Address:
        raise UnsupportedOperation

    def make_share_address(self, stash: Stash, ttl_sec: int | None = None) -> Address:
        raise UnsupportedOperation

    def _save_stash(self, stash: Stash) -> SealedStash:
        raise UnsupportedOperation

    def load_stash(self, address: Address | str) -> SealedStash:
        address = self.parse_address(str(address))

        # TODO: refactor and parse path natively during address construction
        path_regex = r"(?P<name>.*)\.(?P<md5>[a-f0-9]{32})$"
        if not (match := re.match(path_regex, address.path)):
            raise ValueError(f"invalid address: {address}")
        grouped = match.groupdict()
        stash_name = grouped["name"].strip("/")

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
            name=stash_name,
            namespace=address.location.split(".")[0],
            data=data,
        )

        return stash.seal(backend=self, address=address)


@dataclass(frozen=True, kw_only=True)
class HttpAddress(Address):
    scheme: str = "https"
