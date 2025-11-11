from __future__ import annotations

from typing import Iterable
from job_agent_shared import Job


def normalize_greenhouse(board: str, raw_jobs: Iterable[dict]) -> list[Job]:
    jobs: list[Job] = []
    for j in raw_jobs:
        job = Job(
            source="greenhouse",
            source_id=str(j.get("id")),
            url=j.get("absolute_url"),
            title=j.get("title", ""),
            location=(j.get("location") or {}).get("name"),
            description=j.get("content"),
            dept=(j.get("departments") or [{}])[0].get("name") if j.get("departments") else None,
            team=(j.get("offices") or [{}])[0].get("name") if j.get("offices") else None,
        )
        jobs.append(job)
    return jobs


def normalize_lever(org: str, raw_jobs: Iterable[dict]) -> list[Job]:
    jobs: list[Job] = []
    for j in raw_jobs:
        job = Job(
            source="lever",
            source_id=str(j.get("id") or j.get("_id")),
            url=(j.get("hostedUrl") or j.get("applyUrl")),
            title=j.get("text", ""),
            location=(j.get("categories") or {}).get("location"),
            description=j.get("descriptionPlain"),
            dept=(j.get("categories") or {}).get("team"),
            team=(j.get("categories") or {}).get("department"),
        )
        jobs.append(job)
    return jobs


