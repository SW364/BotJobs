"""Generic external source fetcher to integrate third-party job feeds.

Supports configurable endpoints (e.g., RapidAPI connectors for Indeed,
Computrabajo o LinkedIn) returning JSON with job fields. Each source
entry in config.yaml must specify an endpoint and can optionally define
headers/params and mapping keys.
"""
from typing import Dict, List, Any

import requests


DEFAULT_TITLE_KEY = "title"
DEFAULT_COMPANY_KEY = "company"
DEFAULT_LOCATION_KEY = "location"
DEFAULT_URL_KEY = "url"
DEFAULT_DESCRIPTION_KEY = "description"


def _select_records(payload: Any, data_key: str | None) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if data_key and isinstance(payload.get(data_key), list):
            return payload[data_key]
        if isinstance(payload.get("results"), list):
            return payload["results"]
    return []


def _get_value(item: Dict[str, Any], key: str) -> str:
    value = item.get(key)
    if value is None:
        return ""
    return str(value)


def fetch_external_jobs(external_sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    for source in external_sources or []:
        endpoint = source.get("endpoint")
        if not endpoint:
            continue
        headers = source.get("headers") or {}
        params = source.get("params") or {}
        data_key = source.get("data_key")
        title_key = source.get("title_key", DEFAULT_TITLE_KEY)
        company_key = source.get("company_key", DEFAULT_COMPANY_KEY)
        location_key = source.get("location_key", DEFAULT_LOCATION_KEY)
        url_key = source.get("url_key", DEFAULT_URL_KEY)
        description_key = source.get("description_key", DEFAULT_DESCRIPTION_KEY)

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=25)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            continue

        records = _select_records(payload, data_key)
        if not isinstance(records, list):
            continue

        for record in records:
            if not isinstance(record, dict):
                continue
            jobs.append(
                {
                    "title": _get_value(record, title_key),
                    "company": _get_value(record, company_key),
                    "location": _get_value(record, location_key),
                    "url": _get_value(record, url_key),
                    "description": _get_value(record, description_key),
                }
            )
    return jobs
