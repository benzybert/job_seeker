import hashlib
import logging
from typing import Dict, List

from jobspy import scrape_jobs

logger = logging.getLogger(__name__)

def _make_id(job_post) -> str:
    """Generate stable ID from job URL or title+company."""
    url = getattr(job_post, "job_url", None) or ""
    if url:
        return hashlib.sha1(url.encode("utf-8")).hexdigest()
    title = getattr(job_post, "title", "")
    company = getattr(job_post, "company", "")
    return hashlib.sha1(f"{title}-{company}".encode("utf-8")).hexdigest()

def _normalize_job(job_post) -> Dict:
    """Convert JobSpy JobPost to normalized job dict."""
    location_obj = getattr(job_post, "location", None) or {}
    location_str = ""
    if hasattr(location_obj, "city") and location_obj.city:
        location_str = location_obj.city
        if hasattr(location_obj, "state") and location_obj.state:
            location_str += f", {location_obj.state}"
    if hasattr(location_obj, "country") and location_obj.country:
        location_str += f" ({location_obj.country})"

    salary_str = ""
    salary_obj = getattr(job_post, "salary", None)
    if salary_obj:
        min_amt = getattr(salary_obj, "min_amount", None)
        max_amt = getattr(salary_obj, "max_amount", None)
        interval = getattr(salary_obj, "interval", "yearly")
        if min_amt or max_amt:
            salary_str = f"{min_amt or ''}-{max_amt or ''} {interval}"

    description = getattr(job_post, "description", "") or ""

    return {
        "id": _make_id(job_post),
        "title": getattr(job_post, "title", "Unknown"),
        "company": getattr(job_post, "company", ""),
        "location": location_str,
        "url": getattr(job_post, "job_url", ""),
        "description": description,
        "job_type": getattr(job_post, "job_type", None),
        "salary": salary_str,
        "date_posted": getattr(job_post, "date_posted", None),
        "source": "jobspy",
        "raw": job_post,
    }

def fetch_jobspy(cfg: Dict) -> List[Dict]:
    """
    Scrape jobs using JobSpy.
    cfg options:
      enabled: bool
      sites: list of site names (linkedin, indeed, zip_recruiter, google, glassdoor, bayt, naukri, bdjobs)
      search_term: str
      location: str (required for most sites)
      results_wanted: int
      country: str (for Indeed/Glassdoor, e.g. "Israel")
      job_type: str (fulltime, parttime, internship, contract)
      is_remote: bool
      hours_old: int
      proxies: list of proxy strings
      verbose: int (0, 1, 2)
    """
    if not cfg or not cfg.get("enabled", False):
        return []

    sites = cfg.get("sites", ["indeed", "linkedin"])
    search_term = cfg.get("search_term", "software engineer")
    location = cfg.get("location", "Israel")
    results_wanted = int(cfg.get("results_wanted", 50))
    country = cfg.get("country", "Israel")
    job_type = cfg.get("job_type")
    is_remote = cfg.get("is_remote")
    hours_old = cfg.get("hours_old")
    proxies = cfg.get("proxies")
    verbose = int(cfg.get("verbose", 0))

    try:
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            country_indeed=country,
            job_type=job_type,
            is_remote=is_remote,
            hours_old=hours_old,
            proxies=proxies,
            verbose=verbose,
        )
        if jobs_df is None or len(jobs_df) == 0:
            return []
        # Convert DataFrame to list of dicts
        normalized = [_normalize_job(row) for _, row in jobs_df.iterrows()]
        return normalized
    except Exception:
        logger.exception("jobspy_scrape_failed")
        return []