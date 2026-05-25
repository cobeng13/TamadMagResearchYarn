from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal test environments
    yaml = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or Path(__file__).with_name("config.yaml")
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return parse_flat_yaml(text)
    return yaml.safe_load(text) or {}


def parse_flat_yaml(text: str) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip("\"'")
        if value.lower() in {"true", "false"}:
            config[key.strip()] = value.lower() == "true"
        else:
            config[key.strip()] = value
    return config


def env_or_config(config: dict[str, Any], env_name: str, config_name: str | None = None, default: str = "") -> str:
    value = os.getenv(env_name)
    if value is not None:
        return value
    return str(config.get(config_name or env_name.lower(), default) or "")


def enabled_provider(config: dict[str, Any], provider_name: str) -> bool:
    env_name = f"ENABLE_{provider_name.upper()}"
    env_value = os.getenv(env_name)
    if env_value is not None:
        return env_value.strip().lower() in {"1", "true", "yes", "on"}
    value = config.get(env_name.lower())
    if value is None:
        value = config.get(f"enable_{provider_name.lower()}")
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
