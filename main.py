import os
from typing import List, Dict

import yaml
from dotenv import load_dotenv

from filters import apply_filters, ok_link
from messaging import send_report
from sources.greenhouse import fetch_greenhouse_jobs
from sources.lever import fetch_lever_jobs
from sources.external import fetch_external_jobs
from sources.apify_indeed import fetch_apify_indeed_jobs
import storage


CONFIG_PATH = "config.yaml"


def load_config(path: str = CONFIG_PATH) -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def collect_jobs(config: Dict) -> List[Dict[str, str]]:
    greenhouse_tokens = config.get("greenhouse_tokens", [])
    lever_companies = config.get("lever_companies", [])
    external_sources = config.get("external_sources", [])
    apify_indeed_config = config.get("apify_indeed", {})

    jobs: List[Dict[str, str]] = []
    jobs.extend(fetch_greenhouse_jobs(greenhouse_tokens))
    jobs.extend(fetch_lever_jobs(lever_companies))
    jobs.extend(fetch_external_jobs(external_sources))
    apify_token = os.getenv("APIFY_TOKEN")
    jobs.extend(fetch_apify_indeed_jobs(apify_indeed_config, apify_token))
    return jobs


def filter_jobs(jobs: List[Dict[str, str]], filter_config: Dict, seen: set) -> List[Dict[str, str]]:
    filtered: List[Dict[str, str]] = []
    for job in jobs:
        if not apply_filters(job, filter_config):
            continue
        if not ok_link(job.get("url") or ""):
            continue
        if storage.already_seen(job.get("url") or "", seen):
            continue
        filtered.append(job)
    return filtered


def main() -> None:
    load_dotenv()
    config = load_config()
    filter_config = config.get("filters", {})

    seen_jobs = storage.load_seen()
    all_jobs = collect_jobs(config)
    valid_jobs = filter_jobs(all_jobs, filter_config, seen_jobs)

    limit = filter_config.get("limite_envio")
    if limit:
        try:
            limit_value = int(limit)
            valid_jobs = valid_jobs[:limit_value]
        except (TypeError, ValueError):
            pass

    send_report(valid_jobs)

    for job in valid_jobs:
        job_url = job.get("url") or ""
        if job_url:
            storage.mark_seen(job_url, seen_jobs)


if __name__ == "__main__":
    main()
