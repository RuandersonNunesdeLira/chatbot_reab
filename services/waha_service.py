import requests
import os

WAHA_API_URL = os.getenv("WAHA_API_URL")
WAHA_SESSION_NAME = os.getenv("WAHA_SESSION_NAME")

def send_message(chat_id: str, message: str):
    print("num: ", chat_id)

    if not chat_id.startswith("559291618315"):
        return

    if "@" not in chat_id:
        chat_id = f"{chat_id}@c.us"

    headers = {
        "Content-Type": "application/json"
    }

    send_url = f"{WAHA_API_URL}/sendText"

    payload = {
        "session": WAHA_SESSION_NAME,
        "chatId": chat_id,
        "text": message
    }

    return requests.post(url=send_url, headers=headers, json=payload)