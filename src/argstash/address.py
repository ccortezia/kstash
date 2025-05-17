import re
from dataclasses import dataclass, field

# Address segment dentifier allowing alphanumeric, dashs and underscores,
IDENTIFIER_RE = r"[a-zA-Z0-9][a-zA-Z0-9\-_]{0,39}"

NS_RE = rf"(?P<namespace>{IDENTIFIER_RE})"

NAME_RE = rf"(?P<name>{IDENTIFIER_RE})"

MD5_RE = r"[a-f0-9]{32}"

# Common stashes must only contain a namespace and a name.
# - Example: mem://my-namespace/my-variable.28a5e15a666b0cd1415490dcf6674255
GENERAL_ADDRESS_RE = re.compile(
    rf"^(?P<schema>mem|s3)://{NS_RE}/{NAME_RE}\.(?P<md5>{MD5_RE})$"
)

# Inline stashes carry the encoded value directly in the address string.
# - Example: inline://my-namespace/my-variable/MTIzYXNqaGRhYWhzZA==
BASE64_RE = (
    r"(?P<argdata>(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)"
)

INLINE_ADDRESS_RE = re.compile(rf"^(?P<schema>inline)://{NS_RE}/{NAME_RE}/{BASE64_RE}$")


@dataclass(frozen=True, kw_only=True)
class Address:
    schema: str
    namespace: str = "default"
    name: str
    md5: str
    regex: re.Pattern[str] = field(init=False, default=GENERAL_ADDRESS_RE)
    format: str = field(init=False, default="{schema}://{namespace}/{name}.{md5}")

    @classmethod
    def from_string(cls, address: str) -> "Address":
        match = cls.regex.match(address)
        if not match:
            raise ValueError(f"invalid address: {address}")
        return cls(**match.groupdict())

    def __str__(self) -> str:
        return self.format.format(**self.__dict__)


@dataclass(frozen=True, kw_only=True)
class InlineAddress(Address):
    schema: str = "inline"
    namespace: str = "default"
    name: str
    md5: str = ""
    argdata: str
    regex: re.Pattern[str] = field(init=False, default=INLINE_ADDRESS_RE)
    format: str = field(init=False, default="{schema}://{namespace}/{name}/{argdata}")


def address_from_string(address: str) -> Address:
    if address.startswith("inline://"):
        return InlineAddress.from_string(address)
    else:
        return Address.from_string(address)
