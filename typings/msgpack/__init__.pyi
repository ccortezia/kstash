from typing import Any

def packb(
    obj: Any,
    *,
    use_bin_type: bool = True,
    datetime: bool = False,
    unicode_errors: str = "strict",
    use_single_float: bool = False,
    autoreset: bool = True,
    use_float: bool = False,
) -> bytes: ...
def unpackb(
    data: bytes,
    *,
    raw: bool = False,
) -> Any: ...
