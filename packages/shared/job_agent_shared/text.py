from __future__ import annotations

from typing import Iterable


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def combine_text(parts: Iterable[str | None]) -> str:
    combined = " ".join(p for p in parts if p)
    return normalize_text(combined)


def match_filters(text: str, include_any: list[str], include_all: list[str], exclude_any: list[str]) -> bool:
    t = normalize_text(text)
    if exclude_any and any(term.lower() in t for term in exclude_any):
        return False
    if include_all and not all(term.lower() in t for term in include_all):
        return False
    if include_any and not any(term.lower() in t for term in include_any):
        return False
    return True


