import json
import os
from typing import Set


DEFAULT_STORAGE_PATH = "seen_jobs.json"


def load_seen(filepath: str = DEFAULT_STORAGE_PATH) -> Set[str]:
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            return set(data)
    except (json.JSONDecodeError, OSError):
        return set()


def save_seen(seen: Set[str], filepath: str = DEFAULT_STORAGE_PATH) -> None:
    with open(filepath, "w", encoding="utf-8") as handle:
        json.dump(sorted(seen), handle, ensure_ascii=False, indent=2)


def already_seen(url: str, seen: Set[str]) -> bool:
    return url in seen


def mark_seen(url: str, seen: Set[str], filepath: str = DEFAULT_STORAGE_PATH) -> None:
    seen.add(url)
    save_seen(seen, filepath)
