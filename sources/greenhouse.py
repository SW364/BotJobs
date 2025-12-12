import requests


def fetch_greenhouse_jobs(tokens):
    jobs = []
    for token in tokens:
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
        except requests.RequestException:
            continue

        payload = response.json()
        for job in payload.get("jobs", []):
            jobs.append(
                {
                    "title": (job.get("title") or "").strip(),
                    "company": token,
                    "location": ((job.get("location") or {}).get("name")) or "",
                    "url": job.get("absolute_url") or "",
                    "description": job.get("content") or "",
                }
            )
    return jobs
