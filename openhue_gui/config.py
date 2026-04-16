"""Load and save modes configuration."""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from .modes_schema import Config, Mode

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".config" / "openhue-gui"
CONFIG_FILE = CONFIG_DIR / "modes.json"


def ensure_config_dir() -> None:
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load config from JSON file, or return default if missing/invalid."""
    ensure_config_dir()

    if not CONFIG_FILE.exists():
        config = Config.default_config()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        return Config.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Invalid config file: {e}. Using default.")
        return Config.default_config()


def save_config(config: Config) -> None:
    """Save config to JSON file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.to_dict(), f, indent=2)