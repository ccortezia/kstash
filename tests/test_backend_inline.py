import pytest

from argstash.backend_inline import InlineBackend


def test_inline_backend_load_stash_with_incompatible_address_should_raise():
    address = "mem://default/test.28a5e15a666b0cd1415490dcf6674255"
    with pytest.raises(ValueError):
        InlineBackend().load_stash(address)
