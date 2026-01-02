import os
import json
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

bot = Bot(token=BOT_TOKEN)

def safe_send(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print("Telegram send failed:", e)

def run():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    # --------- HARD ENV CHECK ----------
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    if not PORTFOLIO_JSON:
        safe_send(
            f"📊 PORTFOLIO INTELLIGENCE\n🕒 {now}\n\n"
            "❌ PORTFOLIO_JSON variable is EMPTY.\n"
            "Check GitHub → Settings → Variables."
        )
        return

    # --------- PARSE PORTFOLIO ----------
    try:
        portfolio = json.loads(PORTFOLIO_JSON)
    except Exception as e:
        safe_send(
            f"📊 PORTFOLIO INTELLIGENCE\n🕒 {now}\n\n"
            f"❌ Invalid PORTFOLIO_JSON format\n{e}"
        )
        return

    # --------- FETCH DATA (CoinGecko) ----------
    ids = ",".join(portfolio.keys())
    url = "https://api.coingecko.com/api/v3/coins/markets"

    try:
        r = requests.get(
            url,
            params={"vs_currency": "usd", "ids": ids},
            timeout=15
        )
        data = r.json() if r.status_code == 200 else []
    except Exception as e:
        data = []

    if not data:
        safe_send(
            f"📊 PORTFOLIO INTELLIGENCE\n🕒 {now}\n\n"
            "⚠️ CoinGecko returned no data.\n"
            "This is likely rate limiting.\n"
            "Portfolio still loaded successfully."
        )
        return

    # --------- BUILD REPORT ----------
    lines = [
        "📊 PORTFOLIO INTELLIGENCE",
        f"🕒 {now}",
        "",
        "📦 Holdings Overview"
    ]

    for coin in data:
        w = portfolio.get(coin["id"], 0)
        price = coin["current_price"]
        chg = coin.get("price_change_percentage_24h", 0)

        lines.append(
            f"• {coin['symbol'].upper():<5} | {w:.1f}% | "
            f"${price:.2f} | {chg:+.2f}% (24h)"
        )

    # --------- STRATEGY ----------
    lines += [
        "",
        "🧠 STRATEGIC VIEW",
        "• Short-term: Volatility driven, watch BTC correlation",
        "• Mid-term: Heavy L1 + Infra exposure",
        "• Long-term: Strong fundamentals, VET concentration risk"
    ]

    safe_send("\n".join(lines))

if __name__ == "__main__":
    run()
