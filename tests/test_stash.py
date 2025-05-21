import pytest
from kstash.backend_mem import MemBackend
from kstash.stash import Stash


@pytest.mark.parametrize(
    "other",
    [
        pytest.param(
            Stash(name="x", namespace="app", data="data"),
            id="same",
        ),
        pytest.param(
            Stash(name="x", namespace="app", data="data").seal(backend=MemBackend()),
            id="same-sealed",
        ),
    ],
)
def test_stash_eq(other: Stash):
    stash = Stash(name="x", namespace="app", data="data")
    assert stash == other


@pytest.mark.parametrize(
    "other",
    [
        pytest.param(
            Stash(name="y", namespace="app", data="data"),
            id="diff-name",
        ),
        pytest.param(
            Stash(name="x", namespace="other", data="data"),
            id="diff-namespace",
        ),
        pytest.param(
            Stash(name="x", namespace="app", data="other"),
            id="diff-data",
        ),
        pytest.param(
            {"name": "x", "namespace": "app", "data": "data"},
            id="diff-type",
        ),
    ],
)
def test_stash_neq(other: Stash):
    stash = Stash(name="x", namespace="app", data="data")
    assert stash != other


def test_stash_sealed_repr():
    stash = Stash(name="x", namespace="app", data="data").seal(backend=MemBackend())
    expected = "Stash(name=x, namespace=app, address=mem://app/x.266f01c5105567ba27fece1c0383227f)"
    assert repr(stash) == expected
