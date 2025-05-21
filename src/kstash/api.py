from typing import Optional

from .address import Address
from .backend import get_backend_from_address, get_backends_from_config
from .config import CONFIG, Config
from .exceptions import UnsupportedBackend, UnsupportedOperation
from .stash import ArgData, SealedStash


def create(
    name: str,
    data: Optional[ArgData],
    namespace: str = "default",
    config: Config = CONFIG,
) -> SealedStash:
    for backend in get_backends_from_config(config):
        try:
            return backend.save_stash(name, data, namespace)
        except UnsupportedOperation:
            continue
    raise UnsupportedBackend("no backend supports this operation")


def retrieve(
    address: Address | str,
    config: Config = CONFIG,
) -> SealedStash:
    backend = get_backend_from_address(address, config)
    stash = backend.load_stash(address)
    return stash
