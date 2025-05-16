import msgpack
import pytest

from argstash.api import consume, create
from argstash.stash import ArgData


@pytest.mark.parametrize(
    "arg_value",
    [
        pytest.param("red-red", id="alphanumeric"),
        pytest.param('"há não @!;"', id="text"),
        pytest.param(1, id="int"),
        pytest.param(1.0, id="float"),
        pytest.param(True, id="bool"),
    ],
)
def test_echo_inline_stash(arg_value: ArgData):
    stash = create("color", arg_value, namespace="app")
    assert stash.name == "color"
    assert stash.data == arg_value
    assert stash.encoded == msgpack.packb(arg_value)
    assert stash.backend.name == "inline"
    assert stash.namespace == "app"
    assert stash.name == "color"

    stash = consume(stash.address)
    assert stash.name == "color"
    assert stash.data == arg_value
    assert stash.backend.name == "inline"
    assert stash.namespace == "app"
    assert stash.encoded == msgpack.packb(arg_value)
