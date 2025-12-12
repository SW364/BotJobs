import os
from typing import Optional

import requests


TELEGRAM_API_TEMPLATE = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(text: str, bot_token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    destination = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not token or not destination:
        raise ValueError("TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID son requeridos para enviar mensajes")

    payload = {
        "chat_id": destination,
        "text": text,
        "disable_web_page_preview": True,
    }
    url = TELEGRAM_API_TEMPLATE.format(token=token)
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
