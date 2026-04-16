"""Mode data structure and validation."""

import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class Mode:
    """Represents a single lighting mode."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    command: str = ""
    target: str = ""
    target_type: str = "light"  # "light" or "room"
    color: str = "#FFFFFF"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Mode":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            command=data.get("command", ""),
            target=data.get("target", ""),
            target_type=data.get("target_type", "light"),
            color=data.get("color", "#FFFFFF"),
        )


@dataclass
class Config:
    """Configuration container for all modes."""
    version: int = 1
    modes: List[Mode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "modes": [m.to_dict() for m in self.modes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        modes = [Mode.from_dict(m) for m in data.get("modes", [])]
        return cls(
            version=data.get("version", 1),
            modes=modes,
        )

    @classmethod
    def default_config(cls) -> "Config":
        """Create default config with 3 example modes."""
        return cls(
            version=1,
            modes=[
                Mode(name="Warm White", command="--color white --brightness 80", target="", color="#FFFFFF"),
                Mode(name="Cozy Orange", command="--rgb #FF9933 --brightness 60", target="", color="#FF9933"),
                Mode(name="Cool Blue", command="--rgb #3399FF --brightness 70", target="", color="#3399FF"),
            ],
        )