from __future__ import annotations

import json
from typing import Any, Optional

import attrs


@attrs.frozen(kw_only=True)
class ClientInfo:
    ip_address: Optional[str] = None
    serial_port: Optional[str] = None
    override_baudrate: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return attrs.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> ClientInfo:
        return cls(**d)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> ClientInfo:
        return cls.from_dict(json.loads(json_str))
