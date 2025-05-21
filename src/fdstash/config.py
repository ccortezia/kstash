from dataclasses import dataclass, field


# TODO: improve: adopt pydantic
@dataclass(kw_only=True, frozen=True)
class Config:
    max_inline_len: int = 100
    backends: list[str] = field(default_factory=lambda: ["inline", "s3", "https"])
    share_ttl_sec: int = 10

    def __post_init__(self) -> None:
        self._validate_max_inline_len(self.max_inline_len)
        self._validate_backends(self.backends)

    def _validate_max_inline_len(self, max_inline_len: int) -> None:
        if max_inline_len < 1:
            raise ValueError("invalid config (max_inline_len): must be greater than 0")

    def _validate_backends(self, backends: list[str]) -> None:
        if not backends:
            raise ValueError("invalid config (backends): must be non-empty")

        if "inline" in backends and backends.index("inline") != 0:
            raise ValueError("invalid config (backends): inline must come first")


CONFIG = Config()
