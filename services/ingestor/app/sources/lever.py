from __future__ import annotations

from typing import Iterable
import requests


def fetch_lever_org(org_slug: str) -> Iterable[dict]:
    url = f"https://api.lever.co/v0/postings/{org_slug}?mode=json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


