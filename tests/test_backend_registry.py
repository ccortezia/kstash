from dataclasses import dataclass

import pytest
from kstash.backend_base import Backend, BackendRegistry
from kstash.exceptions import UnsupportedBackend


@dataclass(frozen=True)
class DummyBackend(Backend):
    pass


def test_backend_registry_add():
    registry = BackendRegistry()
    registry.add("cls", DummyBackend)
    assert "cls" in registry
    assert registry.get("cls") == DummyBackend


def test_backend_registry_add_duplicate_should_raise():
    registry = BackendRegistry()
    registry.add("cls", DummyBackend)
    with pytest.raises(ValueError, match="'cls' is already registered"):
        registry.add("cls", DummyBackend)


def test_backend_registry_get_unknown_should_raise():
    registry = BackendRegistry()
    with pytest.raises(UnsupportedBackend, match="'unknown' is not registered"):
        registry.get("unknown")


def test_backend_registry_list():
    registry = BackendRegistry()
    initial_backends = set(registry.list())
    registry.add("cls1", DummyBackend)
    registry.add("cls2", DummyBackend)
    assert set(registry.list()) == initial_backends | {"cls1", "cls2"}


def test_backend_registry_contains():
    registry = BackendRegistry()
    registry.add("cls", DummyBackend)
    assert "cls" in registry
    assert "unknown" not in registry
