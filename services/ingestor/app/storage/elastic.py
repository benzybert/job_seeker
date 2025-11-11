from __future__ import annotations

from typing import Iterable
from elasticsearch import Elasticsearch

INDEX_NAME = "jobs-0001"


def get_client(es_url: str) -> Elasticsearch:
    # Dev: security disabled, single-node
    return Elasticsearch(es_url, verify_certs=False)


def ensure_index(es: Elasticsearch) -> None:
    if es.indices.exists(index=INDEX_NAME):
        return
    mapping = {
        "mappings": {
            "properties": {
                "source": {"type": "keyword"},
                "source_id": {"type": "keyword"},
                "url": {"type": "keyword"},
                "dept": {"type": "keyword"},
                "team": {"type": "keyword"},
                "title": {"type": "text"},
                "location": {"type": "text"},
                "description": {"type": "text"},
                "ts": {"type": "date"},
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=mapping)


def bulk_index(es: Elasticsearch, docs: Iterable[dict]) -> None:
    actions = []
    for d in docs:
        actions.append({"index": {"_index": INDEX_NAME}})
        actions.append(d)
    if actions:
        es.bulk(body=actions, refresh="false")


