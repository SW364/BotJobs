import re
from typing import Dict, List

import requests


def ok_link(url: str) -> bool:
    if not url:
        return False
    try:
        response = requests.get(url, allow_redirects=True, timeout=15)
        return 200 <= response.status_code < 400
    except requests.RequestException:
        return False


def _text_contains_any(text: str, keywords: List[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def matches_location(location: str, allowed_locations: List[str]) -> bool:
    if not location:
        return False
    return _text_contains_any(location, allowed_locations)


def matches_title(title: str, allowed_titles: List[str]) -> bool:
    if not title:
        return False
    return _text_contains_any(title, allowed_titles)


def matches_level(text: str, allowed_levels: List[str]) -> bool:
    if not text:
        return False
    return _text_contains_any(text, allowed_levels)


def has_exclusion(text: str, exclusion_terms: List[str]) -> bool:
    if not text:
        return False
    return _text_contains_any(text, exclusion_terms)


def exceeds_years(description: str, threshold: int) -> bool:
    if not description:
        return False
    pattern = re.compile(r"(\d+)\s*(\+|mas|más)?\s*años", re.IGNORECASE)
    for match in pattern.finditer(description):
        try:
            years = int(match.group(1))
        except ValueError:
            continue
        if years >= threshold:
            return True
    return False


def apply_filters(job: Dict[str, str], filter_config: Dict) -> bool:
    title = job.get("title") or ""
    description = job.get("description") or ""
    location = job.get("location") or ""

    allowed_locations = filter_config.get("ubicaciones", [])
    allowed_levels = filter_config.get("niveles", [])
    allowed_titles = filter_config.get("titulos_permitidos", [])
    exclusions = filter_config.get("exclusiones", [])
    years_threshold = int(filter_config.get("exclusion_por_anos", 3))

    text_to_scan = f"{title}\n{description}"

    if not matches_location(location, allowed_locations):
        return False

    if not matches_title(title, allowed_titles):
        return False

    if not matches_level(text_to_scan, allowed_levels):
        return False

    if has_exclusion(text_to_scan, exclusions):
        return False

    if exceeds_years(description, years_threshold):
        return False

    return True
