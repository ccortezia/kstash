from dataclasses import dataclass, field
from typing import Type

from .address import Address, parse_address_scheme
from .config import CONFIG, Config
from .exceptions import UnsupportedBackend, UnsupportedOperation
from .stash import ArgData, LinkedStash, Stash


@dataclass(frozen=True)
class Backend:
    name: str = field(init=False, default=NotImplemented)  # type: ignore

    def save_stash(
        self,
        name: str,
        data: ArgData,
        namespace: str = "default",
        config: Config = CONFIG,
    ) -> LinkedStash:
        if not self._validate_input(data, config):
            raise UnsupportedOperation
        stash = Stash(name=name, namespace=namespace, data=data)
        stash = stash.link(backend=self, address=self.make_address(stash))
        return self._save_stash(stash)

    def _validate_input(self, data: ArgData, config: Config) -> bool:
        return True

    def _save_stash(self, stash: LinkedStash) -> LinkedStash:
        raise NotImplementedError

    def load_stash(self, address: Address | str) -> LinkedStash:
        raise NotImplementedError

    def parse_address(self, address: str) -> Address:
        raise NotImplementedError

    def make_address(self, stash: Stash) -> Address:
        raise NotImplementedError

    def make_share_address(self, stash: Stash, ttl_sec: int = 10) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class BackendRegistry:
    _registry: dict[str, Type["Backend"]] = field(default_factory=dict)

    def add(self, name: str, cls: Type["Backend"]):
        if name in self._registry:
            raise ValueError(f"'{name}' is already registered")
        self._registry[name] = cls

    def get(self, name: str) -> Type["Backend"]:
        try:
            return self._registry[name]
        except KeyError:
            raise UnsupportedBackend(f"'{name}' is not registered")

    def get_from_address(self, address: Address | str) -> Type["Backend"]:
        scheme = parse_address_scheme(address)
        return self.get(scheme)

    def list(self) -> list[str]:
        return list(self._registry.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._registry


BACKEND_REGISTRY = BackendRegistry()


def stash_backend(name: str):
    def wrapper(cls: Type["Backend"]) -> Type["Backend"]:
        BACKEND_REGISTRY.add(name, cls)
        cls.name = name
        return cls

    return wrapper


def get_backend_from_address(address: Address | str, config: Config) -> Backend:
    backend_cls = BACKEND_REGISTRY.get_from_address(address)
    if backend_cls.name not in config.backends:
        raise UnsupportedBackend(f"no backend available to load stash {str(address)}")
    return backend_cls()


def get_backends_from_config(config: Config):
    for backend_name in config.backends:
        backend_cls = BACKEND_REGISTRY.get(backend_name)
        yield backend_cls()
