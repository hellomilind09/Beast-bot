import os
import requests
from datetime import datetime
from telegram import Bot

# ENV
BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

bot = Bot(BOT_TOKEN)

# ---------- COINGECKO HELPERS ----------

def cg(ids):
    return requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ids, "vs_currencies": "usd"}
    ).json()

def narrative_check(category):
    r = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "category": category,
            "price_change_percentage": "7d"
        }
    ).json()

    movers = [
        c for c in r
        if c.get("price_change_percentage_7d", 0) > 15
    ]

    return "Strong" if len(movers) >= 3 else "Weak"

# ---------- SHARED MACRO SCORE (DO NOT REMOVE) ----------

def macro_score():
    prices = cg("bitcoin,ethereum,pax-gold")
    eth = prices["ethereum"]["usd"]
    btc = prices["bitcoin"]["usd"]

    eth_btc = eth / btc

    if eth_btc > 0.075:
        return 70
    elif eth_btc < 0.065:
        return 35
    else:
        return 54

# ---------- MARKET SNAPSHOT ----------

def market_report():
    score = macro_score()

    if score >= 65:
        regime = "Risk-On"
    elif score <= 40:
        regime = "Risk-Off"
    else:
        regime = "Neutral"

    ai = narrative_check("artificial-intelligence")
    rwa = narrative_check("real-world-assets")
    l2 = narrative_check("layer-2")
    depin = narrative_check("depin")
    gaming = narrative_check("gaming")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    msg = f"""
🧠 MARKET SNAPSHOT — GLOBAL VIEW

⏱ Time: {now}
📊 Data: CoinGecko

━━━━━━━━━━━━━━━━━━
🌍 MACRO REGIME
━━━━━━━━━━━━━━━━━━
Risk Regime: {regime}
Macro Score: {score}/100

━━━━━━━━━━━━━━━━━━
🔥 NARRATIVE HEATMAP
━━━━━━━━━━━━━━━━━━
AI / Compute: {ai}
RWA / Tokenization: {rwa}
Layer-2s: {l2}
DePIN / Infra: {depin}
Gaming / Consumer: {gaming}

━━━━━━━━━━━━━━━━━━
🧭 ACTION
━━━━━━━━━━━━━━━━━━
NONE — Observe only
"""

    bot.send_message(
        chat_id=MARKET_CHAT_ID,
        text=msg
    )

# ---------- RUN ----------

if __name__ == "__main__":
    market_report()
