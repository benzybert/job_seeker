from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Job Agent API")

# Simple in-memory store
jobs_store: List[dict] = []

class JobIn(BaseModel):
    id: str
    title: str | None = None
    company: str | None = None
    location: str | None = None
    url: str | None = None
    description: str | None = None
    source: str | None = None

@app.post("/jobs/new", status_code=200)
def receive_job(job: JobIn):
    """Webhook endpoint: ingestor POSTs new jobs here."""
    doc = job.dict()
    # avoid duplicates by id
    if not any(j["id"] == doc["id"] for j in jobs_store):
        jobs_store.append(doc)
    return {"status": "ok", "id": doc["id"]}

@app.get("/jobs", response_model=List[JobIn])
def list_jobs(limit: int = 50):
    """List all jobs."""
    return jobs_store[:limit]

@app.get("/jobs/{job_id}", response_model=JobIn)
def get_job(job_id: str):
    """Get a single job by ID."""
    for job in jobs_store:
        if job["id"] == job_id:
            return job
    return {"error": "not found"}

@app.get("/stats")
def stats():
    """Job stats."""
    return {
        "total_jobs": len(jobs_store),
        "by_source": {
            source: len([j for j in jobs_store if j.get("source") == source])
            for source in set(j.get("source") for j in jobs_store if j.get("source"))
        }
    }