from __future__ import annotations

from typing import Iterable
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from job_agent_shared import JobStatus


def get_collection(mongo_uri: str, db_name: str = "job_agent", collection: str = "jobs") -> Collection:
    client = MongoClient(mongo_uri)
    return client[db_name][collection]


def find_candidates(coll: Collection, limit: int = 10) -> list[dict]:
    # Select NEW or READY
    cursor = coll.find({"status": {"$in": [JobStatus.NEW.value, JobStatus.READY.value]}}).limit(limit)
    return list(cursor)


def mark_status(coll: Collection, job: dict, status: JobStatus, reason: str | None = None) -> None:
    update = {"$set": {"status": status.value, "last_seen": datetime.utcnow()}}
    if reason:
        update["$set"]["apply_reason"] = reason
    coll.update_one({"source": job["source"], "source_id": job["source_id"]}, update)


