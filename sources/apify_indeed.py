"""Integration with Apify Indeed Scraper actor via API v2."""
from __future__ import annotations

import time
from typing import Dict, List, Any

import requests

APIFY_BASE_URL = "https://api.apify.com/v2"
ACT_ID = "apify~indeed-scraper"
DEFAULT_WAIT_SECS = 2
MAX_POLLS = 10


def _run_actor(token: str, input_payload: Dict[str, Any]) -> Dict[str, Any] | None:
    url = f"{APIFY_BASE_URL}/acts/{ACT_ID}/runs"
    try:
        response = requests.post(url, params={"token": token}, json=input_payload, timeout=30)
        response.raise_for_status()
        return response.json().get("data")
    except requests.RequestException:
        return None


def _poll_run(run_id: str, token: str) -> Dict[str, Any] | None:
    url = f"{APIFY_BASE_URL}/actor-runs/{run_id}"
    for _ in range(MAX_POLLS):
        try:
            response = requests.get(url, params={"token": token}, timeout=20)
            response.raise_for_status()
            data = response.json().get("data") or {}
        except requests.RequestException:
            return None
        status = data.get("status")
        if status in {"SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"}:
            return data
        time.sleep(DEFAULT_WAIT_SECS)
    return data if "status" in locals() else None


def _fetch_dataset_items(dataset_id: str, token: str) -> List[Dict[str, Any]]:
    url = f"{APIFY_BASE_URL}/datasets/{dataset_id}/items"
    params = {"token": token, "format": "json"}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
    except requests.RequestException:
        return []
    except ValueError:
        return []
    return []


def _normalize_job(item: Dict[str, Any]) -> Dict[str, str]:
    return {
        "title": str(item.get("title", "")),
        "company": str(item.get("companyName", item.get("company", ""))),
        "location": str(item.get("location", "")),
        "url": str(item.get("url", item.get("shareLink", ""))),
        "description": str(item.get("jobDescription", item.get("description", ""))),
    }


def fetch_apify_indeed_jobs(apify_config: Dict[str, Any], token: str | None) -> List[Dict[str, str]]:
    if not token or not apify_config:
        return []

    queries = apify_config.get("queries") or []
    country = apify_config.get("country", "mx")
    items_limit = apify_config.get("items_limit", 30)
    jobs: List[Dict[str, str]] = []

    for query in queries:
        search_query = query.get("query") if isinstance(query, dict) else None
        location_query = query.get("location") if isinstance(query, dict) else None
        if not search_query:
            continue
        input_payload = {
            "searchQuery": search_query,
            "locationQuery": location_query or "",
            "country": country,
            "jobsLimit": items_limit,
            "maxPages": query.get("max_pages", 1) if isinstance(query, dict) else 1,
            "saveOnlyUniqueItems": True,
        }

        run_data = _run_actor(token, input_payload)
        if not run_data:
            continue
        run_id = run_data.get("id")
        if not run_id:
            continue
        final_run = _poll_run(run_id, token)
        if not final_run or final_run.get("status") != "SUCCEEDED":
            continue
        dataset_id = final_run.get("defaultDatasetId")
        if not dataset_id:
            continue
        dataset_items = _fetch_dataset_items(dataset_id, token)
        for item in dataset_items:
            if not isinstance(item, dict):
                continue
            jobs.append(_normalize_job(item))
    return jobs
