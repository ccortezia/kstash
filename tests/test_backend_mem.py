import pytest
from kstash.backend_mem import MemBackend
from kstash.exceptions import UnsupportedOperation
from kstash.stash import Stash


def test_mem_backend_cannot_share_stash():
    backend = MemBackend()
    with pytest.raises(UnsupportedOperation):
        stash = Stash(name="x", data="config-data")
        backend.make_share_address(stash)
