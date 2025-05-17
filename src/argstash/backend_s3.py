from dataclasses import dataclass

from .address import Address
from .backend_base import Backend, stash_backend
from .stash import Stash


@stash_backend("s3")
@dataclass(frozen=True)
class S3Backend(Backend):
    def _save_stash(self, stash: Stash) -> Stash:
        # TODO: Implement S3 backend.
        return stash

    def load_stash(self, address: Address) -> Stash:
        # TODO: Implement S3 backend.
        raise NotImplementedError
