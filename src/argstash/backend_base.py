from dataclasses import dataclass, field
from typing import Type

from .address import Address, address_from_string
from .config import Config
from .exceptions import UnsupportedBackend
from .stash import ArgData, Stash


@dataclass(frozen=True)
class Backend:
    name: str = field(init=False, default=NotImplemented)  # type: ignore

    def accepts(self, value: ArgData, config: Config) -> bool:
        return True

    def save_stash(self, name: str, data: ArgData, namespace: str = "default") -> Stash:
        stash = Stash(name=name, namespace=namespace, backend=self, data=data)
        return self._save_stash(stash)

    def _save_stash(self, stash: Stash) -> Stash:
        raise NotImplementedError

    def load_stash(self, address: Address) -> Stash:
        raise NotImplementedError

    def make_address(self, stash: Stash) -> Address:
        return Address(
            schema=self.name,
            namespace=stash.namespace,
            name=stash.name,
            md5=stash.md5,
        )


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


def get_backend_from_value(value: ArgData, config: Config) -> Backend:
    for backend_name in config.backends:
        backend_cls = BACKEND_REGISTRY.get(backend_name)
        backend = backend_cls()
        if backend.accepts(value, config):
            return backend
    raise UnsupportedBackend("no backend available")


def get_backend_from_address(address: Address | str, config: Config) -> Backend:
    if isinstance(address, str):
        address = address_from_string(address)
    backend_cls = BACKEND_REGISTRY.get(address.schema)
    return backend_cls()
