from __future__ import annotations

import os
import time
from loguru import logger
from job_agent_shared.logging import setup_logging
from .config import get_settings
from .storage.mongo_repo import get_collection, find_candidates, mark_status
from .apply.chooser import choose_resume
from .apply.email import render_email, build_message, send_email
from job_agent_shared import JobStatus


def process_job(cfg: dict, job: dict) -> None:
    resumes_cfg = cfg.get("resumes", {})
    email_cfg = cfg.get("email", {})
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    template_name = "cover_email.j2"
    resume_url = choose_resume(job, resumes_cfg)
    subject_prefix = email_cfg.get("subject_prefix", "[JobAgent]")
    subject = f'{subject_prefix} Application: {job.get("title")}'
    body = render_email(template_dir, template_name, {"job": job})
    msg = build_message(email_cfg.get("from"), email_cfg.get("to"), subject, body, resume_url)

    if email_cfg.get("dry_run", True) or not email_cfg.get("enabled", True):
        logger.info({"event": "email_dry_run", "job": {"source": job["source"], "id": job["source_id"]}})
    else:
        send_email(
            email_cfg.get("smtp_host"),
            int(email_cfg.get("smtp_port", 587)),
            email_cfg.get("smtp_user"),
            email_cfg.get("smtp_pass"),
            bool(email_cfg.get("use_tls", True)),
            msg,
        )
        logger.info({"event": "email_sent", "job": {"source": job["source"], "id": job["source_id"]}})


def main() -> None:
    setup_logging("sender")
    cfg = get_settings()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    coll = get_collection(mongo_uri)
    rabbit_host = os.getenv("RABBIT_HOST", "rabbitmq")
    qcfg = cfg.get("apply_queue", {})
    poll_seconds = int(cfg.get("runtime", {}).get("poll_seconds", 60))

    logger.info({"event": "sender_started", "queue_enabled": bool(qcfg.get("enabled", False))})

    if qcfg.get("enabled", False):
        # Consume from RabbitMQ (not default for dev)
        from .messaging.rabbit import consume

        def handler(msg: dict) -> None:
            if msg.get("action") != "apply" or "job" not in msg:
                return
            job = msg["job"]
            try:
                process_job(cfg, job)
                mark_status(coll, job, JobStatus.APPLIED)
            except Exception as e:
                logger.exception({"event": "apply_failed", "error": str(e)})
                mark_status(coll, job, JobStatus.FAILED, reason=str(e))

        consume(rabbit_host, qcfg.get("queue_name", "jobs.new"), handler)
    else:
        # Simple polling from Mongo (dev)
        while True:
            try:
                candidates = find_candidates(coll, limit=5)
                for job in candidates:
                    try:
                        process_job(cfg, job)
                        mark_status(coll, job, JobStatus.APPLIED)
                    except Exception as e:
                        logger.exception({"event": "apply_failed", "error": str(e)})
                        mark_status(coll, job, JobStatus.FAILED, reason=str(e))
            except Exception as e:
                logger.exception({"event": "sender_error", "error": str(e)})
            time.sleep(poll_seconds)


if __name__ == "__main__":
    main()


