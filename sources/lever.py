import requests


def fetch_lever_jobs(companies):
    jobs = []
    for company in companies:
        api_url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
        except requests.RequestException:
            continue

        for job in response.json():
            jobs.append(
                {
                    "title": (job.get("text") or "").strip(),
                    "company": job.get("company") or company,
                    "location": (job.get("categories") or {}).get("location") or "",
                    "url": job.get("hostedUrl") or job.get("applyUrl") or "",
                    "description": job.get("descriptionPlain")
                    or job.get("description")
                    or "",
                }
            )
    return jobs
