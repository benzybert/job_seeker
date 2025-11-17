import hashlib
import logging
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
USER_AGENT = "JobAgent/1.0 (+https://github.com/)"

def _make_id(company: str, url: str) -> str:
    return hashlib.sha1(f"{company}-{url}".encode("utf-8")).hexdigest()

def _fetch_company_board(url: str, timeout: int = 10) -> List[Dict]:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    openings = soup.select(".opening")
    out = []
    for o in openings:
        a = o.find("a")
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get("href", "")
        link = href if href.startswith("http") else urljoin("https://boards.greenhouse.io", href)
        loc_node = o.select_one(".location")
        location = loc_node.get_text(strip=True) if loc_node else ""
        out.append({"title": title, "url": link, "location": location, "raw": {"element_html": str(o)}})
    return out

def _is_israel_location(location: str, cities: List[str]) -> bool:
    if not location:
        return False
    loc_up = location.upper()
    if "ISRAEL" in loc_up or "IL" == loc_up.strip():
        return True
    for c in cities:
        if c.upper() == loc_up or c.upper() in loc_up:
            return True
    return False

def fetch_greenhouse(cfg: Dict) -> List[Dict]:
    """
    cfg:
      enabled: bool
      companies: [ "acronis", "..." ]           # optional
      companies_file: "/path/to/file.json"      # optional (in-container path)
      timeout: int
      max_jobs: int
      cities: [ ... ]                           # optional list for city-name matching
    Returns list of normalized job dicts.
    """
    if not cfg or not cfg.get("enabled", False):
        return []

    timeout = int(cfg.get("timeout", 10))
    max_jobs = int(cfg.get("max_jobs", 500))
    cities = cfg.get("cities", [])
    companies = cfg.get("companies") or []

    # optional companies_file
    companies_file = cfg.get("companies_file")
    if companies_file:
        try:
            import json
            with open(companies_file, "r", encoding="utf-8") as fh:
                companies = json.load(fh)
        except Exception:
            logger.exception("failed_read_companies_file")

    jobs = []
    for company in companies:
        if len(jobs) >= max_jobs:
            break
        try:
            board_url = f"https://boards.greenhouse.io/{company}"
            entries = _fetch_company_board(board_url, timeout=timeout)
        except Exception:
            logger.exception("greenhouse_fetch_failed", company=company)
            continue

        for e in entries:
            if len(jobs) >= max_jobs:
                break
            try:
                if not _is_israel_location(e.get("location", ""), cities):
                    continue
                job = {
                    "id": _make_id(company, e["url"]),
                    "title": e.get("title"),
                    "company": company,
                    "location": e.get("location"),
                    "url": e.get("url"),
                    "description": "",  # can fetch job page for detail if needed
                    "source": "greenhouse",
                    "raw": e.get("raw"),
                }
                jobs.append(job)
            except Exception:
                logger.exception("greenhouse_process_job_failed", company=company)
    return jobs