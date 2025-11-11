from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any

DEFAULT_TZ = "Asia/Jerusalem"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _merge_dict(result[k], v)
        else:
            result[k] = v
    return result


def load_settings(service_root: Path) -> dict[str, Any]:
    # Load default, then config.yaml if present, then overlay minimal ENV keys
    default_path = service_root / "config.default.yaml"
    config_path = service_root / "config.yaml"
    data = _load_yaml(default_path)
    data = _merge_dict(data, _load_yaml(config_path))
    # ENV overrides for common settings
    env_overrides = {
        "runtime": {
            "poll_seconds": int(os.getenv("POLL_SECONDS", data.get("runtime", {}).get("poll_seconds", 300))),
            "timezone": os.getenv("TIMEZONE", data.get("runtime", {}).get("timezone", DEFAULT_TZ)),
        },
        "apply_queue": {
            "enabled": os.getenv("APPLY_QUEUE_ENABLED", str(data.get("apply_queue", {}).get("enabled", False))).lower()
            in {"1", "true", "yes"},
            "queue_name": os.getenv("APPLY_QUEUE_NAME", data.get("apply_queue", {}).get("queue_name", "jobs.new")),
        },
        "email": {
            "enabled": os.getenv("EMAIL_ENABLED", str(data.get("email", {}).get("enabled", True))).lower()
            in {"1", "true", "yes"},
            "dry_run": os.getenv("EMAIL_DRY_RUN", str(data.get("email", {}).get("dry_run", True))).lower()
            in {"1", "true", "yes"},
            "from": os.getenv("EMAIL_FROM", data.get("email", {}).get("from")),
            "to": os.getenv("EMAIL_TO", data.get("email", {}).get("to")),
            "subject_prefix": os.getenv("EMAIL_SUBJECT_PREFIX", data.get("email", {}).get("subject_prefix", "[JobAgent]")),
            "smtp_host": os.getenv("SMTP_HOST", data.get("email", {}).get("smtp_host")),
            "smtp_port": int(os.getenv("SMTP_PORT", data.get("email", {}).get("smtp_port", 587))),
            "smtp_user": os.getenv("SMTP_USER", data.get("email", {}).get("smtp_user")),
            "smtp_pass": os.getenv("SMTP_PASS", data.get("email", {}).get("smtp_pass")),
            "use_tls": os.getenv("SMTP_USE_TLS", str(data.get("email", {}).get("use_tls", True))).lower()
            in {"1", "true", "yes"},
        },
    }
    return _merge_dict(data, env_overrides)


