from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from winregistry.consts import WinregType


@dataclass(frozen=True)
class RegEntry:
    name: str
    reg_key: str
    value: Any
    type: WinregType
    host: Optional[str] = None


@dataclass(frozen=True)
class RegKey:
    name: str
    reg_keys: List[str]
    entries: List[RegEntry]
    modify_at: datetime
