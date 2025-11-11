from __future__ import annotations

from job_agent_shared import combine_text


def choose_resume(job: dict, resumes_cfg: dict) -> str:
    """
    Very simple keyword-based chooser; returns s3 url string.
    """
    text = combine_text([job.get("title"), job.get("description")])
    text_l = text.lower()
    if any(k in text_l for k in ["data", "ml", "analytics", "etl"]):
        return resumes_cfg.get("data")
    if any(k in text_l for k in ["backend", "server", "python", "api"]):
        return resumes_cfg.get("backend")
    return resumes_cfg.get("fullstack")


