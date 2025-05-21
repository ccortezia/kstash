import pytest
from kstash.backend import get_backend_from_address
from kstash.config import CONFIG, Config
from kstash.exceptions import UnsupportedBackend


@pytest.mark.parametrize(
    "address,backend_name",
    [
        pytest.param("inline://ns/x/cmVkICAxMQ==", "inline", id="inline"),
        pytest.param("mem://ns/x.28a5e15a666b0cd1415490dcf6674255", "mem", id="mem"),
        pytest.param("s3://ns/x.28a5e15a666b0cd1415490dcf6674255", "s3", id="s3"),
    ],
)
def test_get_backend_from_address(address: str, backend_name: str):
    config = Config(backends=["inline", "mem", "s3"])
    backend = get_backend_from_address(address, config)
    assert backend.name == backend_name


def test_get_backend_from_address_unsupported_schema_should_raise():
    with pytest.raises(UnsupportedBackend):
        get_backend_from_address("unknown://default/test/cmVkICAxMQ==", CONFIG)
