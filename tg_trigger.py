import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("ACTION_CHAT_ID")  # reuse action chat
GH_TOKEN = os.getenv("GH_TOKEN")

OWNER = "YOUR_GITHUB_USERNAME"
REPO = "YOUR_REPO_NAME"
WORKFLOW_FILE = "beast-bot.yml"  # exact workflow filename
BRANCH = "main"

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
GH_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"

def send(msg):
    requests.post(TG_URL, json={"chat_id": CHAT_ID, "text": msg})

def trigger(workflow_input):
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "ref": BRANCH,
        "inputs": workflow_input
    }
    r = requests.post(GH_URL, headers=headers, json=payload)
    return r.status_code

def main(command):
    if command == "market":
        code = trigger({"mode": "market"})
        send("🧠 Market bot triggered")
    elif command == "action":
        code = trigger({"mode": "action"})
        send("⚡ Action bot triggered")
    elif command == "portfolio":
        code = trigger({"mode": "portfolio"})
        send("📊 Portfolio bot triggered")
    elif command == "runall":
        code = trigger({"mode": "all"})
        send("🚀 All bots triggered")
    else:
        send("❓ Unknown command")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
