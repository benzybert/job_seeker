from __future__ import annotations

from typing import Iterable
import requests


def fetch_greenhouse_board(board_token: str) -> Iterable[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("jobs", [])


