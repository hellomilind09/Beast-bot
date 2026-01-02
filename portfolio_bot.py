import os
from datetime import datetime
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
    print("Telegram status:", r.status_code)

now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

msg = f"""
🧪 PORTFOLIO BOT DEBUG

Time: {now}

BOT_TOKEN present: {"YES" if BOT_TOKEN else "NO"}
CHAT_ID present: {"YES" if CHAT_ID else "NO"}
PORTFOLIO_JSON present: {"YES" if PORTFOLIO_JSON else "NO"}

PORTFOLIO_JSON value:
{PORTFOLIO_JSON}
"""

print(msg)

if BOT_TOKEN and CHAT_ID:
    send(msg)
else:
    print("Missing BOT_TOKEN or CHAT_ID")
