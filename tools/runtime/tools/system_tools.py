from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class SystemTool:
    name: str
    fn: Callable[..., Any]


def register_system_tools():
    pass
