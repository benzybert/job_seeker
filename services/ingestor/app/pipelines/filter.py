from __future__ import annotations

from job_agent_shared import combine_text, match_filters, Job


def filter_jobs(jobs: list[Job], include_any: list[str], include_all: list[str], exclude_any: list[str]) -> list[Job]:
    passed: list[Job] = []
    for job in jobs:
        text = combine_text([job.title, job.location, job.description])
        if match_filters(text, include_any, include_all, exclude_any):
            passed.append(job)
    return passed


