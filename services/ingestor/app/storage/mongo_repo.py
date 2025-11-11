from __future__ import annotations

from datetime import datetime
from typing import Any
from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from job_agent_shared import Job, CURRENT_SCHEMA_VERSION


def get_collection(mongo_uri: str, db_name: str = "job_agent", collection: str = "jobs") -> Collection:
    client = MongoClient(mongo_uri)
    coll = client[db_name][collection]
    coll.create_index([("source", 1), ("source_id", 1)], unique=True)
    coll.create_index([("ts", -1)])
    coll.create_index([("title", "text"), ("location", "text"), ("description", "text")])
    return coll


def upsert_jobs(coll: Collection, jobs: list[Job]) -> dict[str, Any]:
    now = datetime.utcnow()
    ops: list[UpdateOne] = []
    for job in jobs:
        doc = job.model_dump()
        doc["schema_version"] = CURRENT_SCHEMA_VERSION
        ops.append(
            UpdateOne(
                {"source": job.source, "source_id": job.source_id},
                {
                    "$setOnInsert": {"first_seen": now},
                    "$set": {
                        **{k: v for k, v in doc.items() if k not in {"first_seen"}},
                        "last_seen": now,
                    },
                },
                upsert=True,
            )
        )
    if not ops:
        return {"matched": 0, "modified": 0, "upserted": 0}
    result = coll.bulk_write(ops, ordered=False)
    return {
        "matched": result.matched_count,
        "modified": result.modified_count,
        "upserted": len(result.upserted_ids or {}),
    }


