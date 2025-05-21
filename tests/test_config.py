import pytest
from kstash.config import Config


def test_default_config():
    config = Config()
    assert config.max_inline_len == 100
    assert config.backends == ["inline", "s3", "https"]


def test_custom_config():
    config = Config(max_inline_len=200, backends=["inline", "s3", "custom"])
    assert config.max_inline_len == 200
    assert config.backends == ["inline", "s3", "custom"]


def test_invalid_max_inline_len():
    with pytest.raises(
        ValueError, match="invalid config \\(max_inline_len\\): must be greater than 0"
    ):
        Config(max_inline_len=0)

    with pytest.raises(
        ValueError, match="invalid config \\(max_inline_len\\): must be greater than 0"
    ):
        Config(max_inline_len=-1)


def test_invalid_empty_backends():
    with pytest.raises(
        ValueError, match="invalid config \\(backends\\): must be non-empty"
    ):
        Config(backends=[])


def test_invalid_inline_backend_position():
    with pytest.raises(
        ValueError, match="invalid config \\(backends\\): inline must come first"
    ):
        Config(backends=["s3", "inline"])

    with pytest.raises(
        ValueError, match="invalid config \\(backends\\): inline must come first"
    ):
        Config(backends=["s3", "inline", "custom"])
