from __future__ import annotations

import os
import time
from loguru import logger
from job_agent_shared import combine_text
from .logging import setup_logging
from .config import get_settings
from .sources.greenhouse import fetch_greenhouse_board
from .sources.lever import fetch_lever_org
from .pipelines.normalize import normalize_greenhouse, normalize_lever
from .pipelines.filter import filter_jobs
from .storage.mongo_repo import get_collection, upsert_jobs
from .storage.elastic import get_client as es_client, ensure_index, bulk_index
from .messaging.rabbit import publish


def main() -> None:
    setup_logging("ingestor")
    cfg = get_settings()

    poll_seconds = int(cfg["runtime"]["poll_seconds"])
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    es_url = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
    rabbit_host = os.getenv("RABBIT_HOST", "rabbitmq")

    coll = get_collection(mongo_uri)
    es = es_client(es_url)
    ensure_index(es)

    logger.info({"event": "ingestor_started", "poll_seconds": poll_seconds})

    while True:
        try:
            # Fetch sources
            gh_tokens = cfg.get("sources", {}).get("greenhouse", {}).get("boards", [])
            lever_orgs = cfg.get("sources", {}).get("lever", {}).get("orgs", [])
            all_jobs = []
            for b in gh_tokens:
                raw = fetch_greenhouse_board(b)
                all_jobs.extend(normalize_greenhouse(b, raw))
            for org in lever_orgs:
                raw = fetch_lever_org(org)
                all_jobs.extend(normalize_lever(org, raw))

            # Filter
            filters = cfg.get("filters", {})
            include_any = filters.get("include_any", [])
            include_all = filters.get("include_all", [])
            exclude_any = filters.get("exclude_any", [])
            filtered = filter_jobs(all_jobs, include_any, include_all, exclude_any)

            # Persist + index
            result = upsert_jobs(coll, filtered)
            bulk_index(es, [j.model_dump() for j in filtered])
            logger.info({"event": "ingestor_cycle", "fetched": len(all_jobs), "filtered": len(filtered), **result})

            # Optional queue publish
            apply_queue = cfg.get("apply_queue", {})
            if apply_queue.get("enabled"):
                qname = apply_queue.get("queue_name", "jobs.new")
                for j in filtered:
                    publish(
                        rabbit_host,
                        qname,
                        {"action": "apply", "job": {"source": j.source, "id": j.source_id, "url": j.url}},
                    )
        except Exception as e:
            logger.exception({"event": "ingestor_error", "error": str(e)})

        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()


