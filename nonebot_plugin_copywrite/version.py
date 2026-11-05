"""插件版本，以及 `__min_version__` 的比较。"""

import re
from importlib.metadata import PackageNotFoundError, version

try:
    PLUGIN_VERSION = version("nonebot-plugin-copywrite")
except PackageNotFoundError:
    PLUGIN_VERSION = "0.0.0"


def parse_version(value: object) -> tuple[int, int, int]:
    """取前三段数字，`0.3` 与 `0.3.0` 等价，`0.3.3a1` 视为 `0.3.3`。"""
    parts = [int(i) for i in re.findall(r"\d+", str(value))[:3]]
    return tuple(parts + [0] * (3 - len(parts)))  # type: ignore[return-value]


def satisfies(min_version: object) -> bool:
    """当前插件版本是否不低于 min_version。"""
    return parse_version(PLUGIN_VERSION) >= parse_version(min_version)
