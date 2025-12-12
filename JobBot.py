# main.py
import os, re, yaml, requests
from dataclasses import dataclass
from typing import List, Optional

TIMEOUT = 12

@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    description: str = ""

KEYWORDS = ["python","django","javascript","react","sql","mysql","kotlin","android","git","rest","api"]

def ok_link(url: str) -> bool:
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent":"job-scout/1.0"})
        return 200 <= r.status_code < 400
    except requests.RequestException:
        return False

def greenhouse_jobs(board_token: str) -> List[Job]:
    api = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    r = requests.get(api, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out = []
    for j in data.get("jobs", []):
        out.append(Job(
            title=j.get("title","").strip(),
            company=board_token,  # opcional: map token->company real
            location=(j.get("location",{}) or {}).get("name","").strip(),
            url=j.get("absolute_url","").strip(),
            description=(j.get("content","") or "")
        ))
    return out

def lever_jobs(company: str) -> List[Job]:
    api = f"https://api.lever.co/v0/postings/{company}?mode=json"
    r = requests.get(api, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out = []
    for j in data:
        loc = (j.get("categories",{}) or {}).get("location","") or ""
        out.append(Job(
            title=(j.get("text") or "").strip(),
            company=company,
            location=loc.strip(),
            url=(j.get("hostedUrl") or "").strip(),
            description=(j.get("descriptionPlain") or j.get("description") or "")
        ))
    return out

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def passes_filters(job: Job, cfg: dict) -> bool:
    f = cfg["filters"]
    t = normalize(job.title)
    loc = normalize(job.location)
    desc = normalize(job.description)

    # título debe contener algo
    if not any(normalize(x) in t for x in f["titles_must_include"]):
        return False

    # ubicación: Monterrey/NL o remoto MX (heurística)
    if not any(normalize(x) in loc for x in f["locations"]):
        return False

    # excluir senior/lead
    if any(x in t for x in ["senior","sr","lead","staff","principal","manager"]):
        return False

    # excluir por años (heurística simple)
    m = re.search(r"(\d+)\+?\s*(años|years)", desc)
    if m and int(m.group(1)) >= f["exclude_if_years_gte"]:
        return False

    return True

def make_message(job: Job, cfg: dict) -> str:
    profile = cfg["profile"]["pitch"]
    jd = normalize(job.description)
    hits = [k for k in KEYWORDS if k in jd][:4]  # pocas para no pasar 300 chars
    stack = ", ".join(h.upper() if h in ["sql","api"] else h.title() for h in hits) or "Python/Django y React"

    msg = (f"Hola, vi la vacante de {job.title} en {job.company}. "
           f"Tengo base sólida en {stack} y experiencia con Git y APIs REST. "
           f"Me interesa aportar en features y mejoras. ¿Te parece si conectamos para platicar?")
    return msg[:300]

def send_telegram(text: str):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=TIMEOUT).raise_for_status()

def format_report(jobs: List[Job], cfg: dict) -> str:
    lines = [f"Encontré {len(jobs)} vacantes (links verificados):\n"]
    for j in jobs:
        lines += [
            f"- {j.title} | {j.company} | {j.location}",
            f"  Link: {j.url}",
            f"  Mensaje: {make_message(j, cfg)}",
            ""
        ]
    return "\n".join(lines)

def main():
    cfg = yaml.safe_load(open("config.yaml", "r", encoding="utf-8"))

    # TODO: llena estos tokens/companies con tu lista objetivo (o mantén un archivo)
    greenhouse_tokens = ["acme"]   # reemplaza
    lever_companies = ["xmlexample"]  # reemplaza

    jobs: List[Job] = []
    for tok in greenhouse_tokens:
        jobs += greenhouse_jobs(tok)
    for c in lever_companies:
        jobs += lever_jobs(c)

    # filtros + link check
    filtered = []
    for j in jobs:
        if passes_filters(j, cfg) and j.url and ok_link(j.url):
            filtered.append(j)

    report = format_report(filtered[:25], cfg)  # limita
    method = cfg["notify"]["method"]
    if method == "telegram":
        send_telegram(report)
    else:
        print(report)  # placeholder para email/sms

if __name__ == "__main__":
    main()
