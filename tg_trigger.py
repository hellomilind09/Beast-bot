import os
import requests
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
ACTION_CHAT_ID = os.getenv("ACTION_CHAT_ID")
GH_TOKEN = os.getenv("GH_TOKEN")

OWNER = "YOUR_GITHUB_USERNAME"
REPO = "YOUR_REPO_NAME"
WORKFLOW_FILE = "beast-bot.yml"
BRANCH = "main"

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
GH_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"

def send(msg):
    requests.post(
        TG_URL,
        json={"chat_id": ACTION_CHAT_ID, "text": msg},
        timeout=10
    )

def trigger(mode):
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "ref": BRANCH,
        "inputs": {"mode": mode}
    }
    r = requests.post(GH_URL, headers=headers, json=payload, timeout=10)
    return r.status_code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        send("❌ No command provided")
        sys.exit(1)

    mode = sys.argv[1]

    if mode not in ["market", "action", "portfolio", "all"]:
        send("❌ Invalid command")
        sys.exit(1)

    code = trigger(mode)

    if code == 204:
        send(f"🚀 Triggered `{mode}` bot successfully")
    else:
        send(f"❌ Failed to trigger `{mode}` bot (HTTP {code})")
