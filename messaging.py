from typing import List

from notify.telegram import send_message

TECH_KEYWORDS = [
    "Python",
    "Django",
    "React",
    "JavaScript",
    "SQL",
    "MySQL",
    "Kotlin",
    "Android",
    "Git",
    "REST",
    "REST API",
]


def extract_keywords(description: str) -> List[str]:
    found = []
    lowered = (description or "").lower()
    for keyword in TECH_KEYWORDS:
        if keyword.lower() in lowered:
            found.append(keyword)
    return found


def build_personal_message(job: dict) -> str:
    keywords = extract_keywords(job.get("description") or "")
    stack_text = ", ".join(keywords) if keywords else "tu stack"
    message = (
        f"Hola, vi la vacante de {job.get('title', '')} en {job.get('company', '')}. "
        f"Tengo experiencia con {stack_text} y proyectos remotos. ¿Te parece si conectamos "
        "para platicar y ver si encaja?"
    )
    if len(message) > 300:
        message = message[:297] + "..."
    return message


def format_job_entry(job: dict) -> str:
    personal_message = build_personal_message(job)
    return (
        f"Título: {job.get('title', '')}\n"
        f"Empresa: {job.get('company', '')}\n"
        f"Ubicación: {job.get('location', '')}\n"
        f"Link: {job.get('url', '')}\n"
        f"Mensaje: {personal_message}\n"
    )


def chunk_text(text: str, max_length: int = 3500) -> List[str]:
    chunks: List[str] = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current.rstrip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.rstrip())
    return chunks


def send_report(jobs: List[dict]) -> None:
    if not jobs:
        return
    entries = [format_job_entry(job) for job in jobs]
    report_text = "\n".join(entries)
    for chunk in chunk_text(report_text):
        send_message(chunk)
