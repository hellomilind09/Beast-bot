from datetime import datetime
import requests
import os
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

bot = Bot(BOT_TOKEN)

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
    movers = [c for c in r if c.get("price_change_percentage_7d", 0) > 15]
    return "Strong" if len(movers) >= 3 else "Weak"

def market_report():
    prices = cg("bitcoin,ethereum,pax-gold")

    eth_btc = prices["ethereum"]["usd"] / prices["bitcoin"]["usd"]
    gold = prices["pax-gold"]["usd"]

    if eth_btc > 0.075:
        regime = "Risk-On"
        macro_score = 70
    elif eth_btc < 0.065:
        regime = "Risk-Off"
        macro_score = 35
    else:
        regime = "Neutral"
        macro_score = 54

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
Macro Score: {macro_score}/100

━━━━━━━━━━━━━━━━━━
🔥 NARRATIVE HEATMAP
━━━━━━━━━━━━━━━━━━
AI / Compute: {ai}
RWA / Tokenization: {rwa}
Layer-2s: {l2}
DePIN / Infra: {depin}
Gaming / Consumer: {gaming}

━━━━━━━━━━━━━━━━━━
🏦 MACRO PROXY
━━━━━━━━━━━━━━━━━━
Gold Proxy: {"Rising" if gold > 2000 else "Stable"}

━━━━━━━━━━━━━━━━━━
🧭 ACTION
━━━━━━━━━━━━━━━━━━
NONE — Observe only
"""

    bot.send_message(chat_id=MARKET_CHAT_ID, text=msg)
