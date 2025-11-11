from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class JobStatus(str, Enum):
    NEW = "NEW"
    READY = "READY"
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"


class Job(BaseModel):
    source: str
    source_id: str
    url: HttpUrl
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    dept: Optional[str] = None
    team: Optional[str] = None
    ts: datetime = Field(default_factory=datetime.utcnow)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    status: JobStatus = JobStatus.NEW
    schema_version: int = 1


class ApplyTask(BaseModel):
    action: str = "apply"
    job: Job

