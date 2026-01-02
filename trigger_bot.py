import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")

OWNER = "hellomilind09"          # your GitHub username
REPO = "Beast-bot"               # your repo name
WORKFLOW = "beast-bot.yml"       # workflow filename
BRANCH = "main"

GH_API = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW}/dispatches"

HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}

async def trigger_workflow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.lower()

    payload = {"ref": BRANCH}

    r = requests.post(GH_API, headers=HEADERS, json=payload)

    if r.status_code == 204:
        await update.message.reply_text(
            f"✅ Workflow triggered via `{cmd}`\n⏳ Bots will post shortly."
        )
    else:
        await update.message.reply_text(
            f"❌ Trigger failed ({r.status_code})\n{r.text}"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("market", trigger_workflow))
    app.add_handler(CommandHandler("action", trigger_workflow))
    app.add_handler(CommandHandler("portfolio", trigger_workflow))
    app.add_handler(CommandHandler("run", trigger_workflow))

    app.run_polling()

if __name__ == "__main__":
    main()
