from typing import Optional

from .address import Address, address_from_string
from .backend import get_backend_from_address, get_backend_from_value
from .config import CONFIG, Config
from .stash import ArgData, Stash


def create(
    name: str,
    value: Optional[ArgData],
    namespace: str = "default",
    config: Config = CONFIG,
) -> Stash:
    backend = get_backend_from_value(value, config)
    stash = backend.save_stash(name, value, namespace)
    return stash


def consume(
    address: Address | str,
    config: Config = CONFIG,
) -> Stash:
    if isinstance(address, str):
        address = address_from_string(address)
    backend = get_backend_from_address(address, config)
    stash = backend.load_stash(address)
    return stash
