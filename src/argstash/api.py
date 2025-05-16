from typing import Optional

from .address import Address
from .backend import get_backend_from_address, get_backend_from_value
from .stash import ArgData, Stash


def create(name: str, value: Optional[ArgData], namespace: str = "default") -> Stash:
    backend = get_backend_from_value(value)
    stash = backend.save_stash(name, value, namespace)
    return stash


def consume(address: Address) -> Stash:
    backend = get_backend_from_address(address)
    stash = backend.load_stash(address)
    return stash
