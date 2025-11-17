import json
import hashlib
import logging
import re
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_START_URL = "https://www.comeet.com/jobs"
USER_AGENT = "JobAgent/1.0 (+https://github.com/)"

# simple city list — extend if needed
DEFAULT_ISRAEL_CITIES = {
    "TEL AVIV", "TLV", "JERUSALEM", "HAIFA", "HERZLIYA", "HERZLIYA-PALO", "BEER SHEVA", "BEERSHEBA",
    "RA'ANANA", "RAANANA", "NETANYA", "ASHDOD", "ASHKELON", "RAMAT GAN", "RAMATGAN"
}

# regex to match COMPANY_POSITIONS_DATA = [...]
_JSON_PATTERN = re.compile(r"COMPANY_POSITIONS_DATA\s*=\s*(\[[\s\S]*?\]);", re.M)

def _make_id(company_name: str, uid: str) -> str:
    return hashlib.sha1(f"{company_name}-{uid}".encode("utf-8")).hexdigest()

def _get_soup(url: str, timeout: int = 10) -> BeautifulSoup:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def _extract_company_urls(start_url: str, timeout: int = 10) -> List[str]:
    try:
        soup = _get_soup(start_url, timeout=timeout)
    except Exception:
        return []
    anchors = soup.find_all("a", href=True)
    urls = []
    for a in anchors:
        href = a["href"]
        if "/jobs/" in href:
            full = urljoin(start_url, href)
            # avoid duplicates
            if full not in urls:
                urls.append(full)
    return urls

def _is_job_in_israel(job: Dict) -> bool:
    # job may have location object
    loc = job.get("location") or {}
    country = (loc.get("country") or "").upper()
    city = (loc.get("city") or "").upper()
    loc_name = (loc.get("name") or "").upper()
    if "ISRAEL" in country or country == "IL":
        return True
    if any(city == c for c in DEFAULT_ISRAEL_CITIES):
        return True
    if "ISRAEL" in loc_name:
        return True
    # fallback: check company meta or other fields
    text_fields = " ".join(str(job.get(k, "")).upper() for k in ("name", "description", "department"))
    return "ISRAEL" in text_fields

def fetch_comeet(cfg: Dict) -> List[Dict]:
    """
    Fetch Comeet jobs.
    cfg options:
      enabled: bool
      start_url: str (page that lists companies) OR
      company_urls: [ ... ] explicit company pages to fetch
      timeout: int
      max_jobs: int
    """
    if not cfg or not cfg.get("enabled", False):
        return []

    timeout = int(cfg.get("timeout", 10))
    max_jobs = int(cfg.get("max_jobs", 200))
    company_urls = cfg.get("company_urls") or []
    start_url = cfg.get("start_url") or DEFAULT_START_URL

    if not company_urls:
        company_urls = _extract_company_urls(start_url, timeout=timeout)

    jobs_out = []
    for url in company_urls:
        if len(jobs_out) >= max_jobs:
            break
        try:
            soup = _get_soup(url, timeout=timeout)
        except Exception:
            logger.debug("comeet_fetch_failed", url=url, exc_info=True)
            continue

        # find COMPANY_POSITIONS_DATA in script tags
        matched = None
        for script in soup.find_all("script", src=False):
            text = script.string or script.text or ""
            m = _JSON_PATTERN.search(text)
            if m:
                matched = m.group(1)
                break

        if not matched:
            continue

        try:
            entries = json.loads(matched)
        except Exception:
            logger.exception("comeet_json_parse_failed", url=url)
            continue

        for job in entries:
            if len(jobs_out) >= max_jobs:
                break
            try:
                if not _is_job_in_israel(job):
                    continue
                title = job.get("name") or job.get("title") or ""
                company = job.get("company_name") or ""
                uid = str(job.get("uid") or job.get("id") or "")
                link = job.get("url_comeet_hosted_page") or job.get("url") or url
                description = job.get("description") or job.get("summary") or ""
                location = (job.get("location") or {}).get("name") or ""
                job_doc = {
                    "id": _make_id(company, uid),
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": link,
                    "description": description,
                    "source": "comeet",
                    "raw": job,
                }
                jobs_out.append(job_doc)
            except Exception:
                logger.exception("comeet_job_process_failed", url=url)

    return jobs_out