from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlparse

if TYPE_CHECKING:
    from .stash import Stash


@dataclass(frozen=True, kw_only=True)
class Address:
    scheme: str
    location: str
    path: str
    extra: list[tuple[str, str]] = field(default_factory=list)

    @classmethod
    def from_string(cls, address: str) -> "Address":
        raise NotImplementedError

    @classmethod
    def from_stash(cls, stash: "Stash") -> "Address":
        raise NotImplementedError

    def __str__(self) -> str:
        url = "/".join([self.location.strip("/"), self.path.strip("/")])
        url = f"{self.scheme}://{url}"
        if self.extra:
            url = "?".join([url, urlencode(self.extra)])
        return url


def parse_address_scheme(address: Address | str) -> str:
    if isinstance(address, Address):
        return address.scheme
    return urlparse(address).scheme
