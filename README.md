Job Agent Monorepo
===================

A production-ready monorepo for a Job Application Agent with two Python services:
- ingestor: fetches jobs from Greenhouse/Lever, normalizes, filters, persists to MongoDB, indexes to Elasticsearch, optional queue publish.
- sender: selects candidate jobs, chooses resume, renders email with Jinja2 template, and dry-runs (or sends) via SMTP; optional RabbitMQ consumption.

Quickstart (Dev)
----------------
1) docker compose up -d
2) For each service, optionally copy config.default.yaml to config.yaml and adjust orgs/boards/filters/emails
3) Open MinIO console (http://localhost:9001), create bucket 'resumes', upload sample PDFs (backend.pdf, fullstack.pdf, data.pdf)
4) Verify Mongo and ES populated; view in Kibana (http://localhost:5601)
5) Sender runs in dry-run mode; switch to real SMTP by toggling config/env

Architecture (ASCII)
--------------------
MongoDB <-> Ingestor -> Elasticsearch
                 \-> RabbitMQ (optional) -> Sender
                                \-> SMTP (email dry-run or real)
MinIO (S3) provides resume PDFs for attachments.

Notes
-----
- Dev: queue disabled, sender polls Mongo, dry-run email.
- Staging/Prod: queue enabled (RabbitMQ), real SMTP with SPF/DKIM/DMARC.
- Respect site TOS/robots; never attempt CAPTCHA bypass.

