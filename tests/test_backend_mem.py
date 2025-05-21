import pytest

from fdstash.backend_mem import MemBackend
from fdstash.exceptions import UnsupportedOperation
from fdstash.stash import Stash


def test_mem_backend_cannot_share_stash():
    backend = MemBackend()
    with pytest.raises(UnsupportedOperation):
        stash = Stash(name="x", data="config-data")
        backend.make_share_address(stash)
