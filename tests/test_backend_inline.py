import pytest
from kstash.backend_inline import InlineBackend
from kstash.exceptions import UnsupportedOperation
from kstash.stash import Stash


def test_inline_backend_load_stash_with_incompatible_address_should_raise():
    address = "mem://default/test.28a5e15a666b0cd1415490dcf6674255"
    with pytest.raises(ValueError):
        InlineBackend().load_stash(address)


def test_inline_backend_cannot_share_stash():
    backend = InlineBackend()
    with pytest.raises(UnsupportedOperation):
        stash = Stash(name="x", data="config-data")
        backend.make_share_address(stash)
