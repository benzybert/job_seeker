from __future__ import annotations

from pathlib import Path
from job_agent_shared import load_settings


def get_settings() -> dict:
    service_root = Path(__file__).resolve().parent.parent
    return load_settings(service_root)


