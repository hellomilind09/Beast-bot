import os
import requests
import schedule
import time
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

bot = Bot(BOT_TOKEN)

def cg(ids):
    return requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ids, "vs_currencies": "usd"}
    ).json()

def macro_score():
    prices = cg("bitcoin,ethereum,pax-gold")
    score = 50

    if prices["ethereum"]["usd"] / prices["bitcoin"]["usd"] > 0.07:
        score += 20

    if prices["pax-gold"]["usd"] > 2000:
        score -= 15

    return score

def narrative_check(category):
    r = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "category": category,
            "price_change_percentage": "7d"
        }
    ).json()

    return len([c for c in r if c.get("price_change_percentage_7d", 0) > 15])

def market_report():
    macro = macro_score()
    ai = narrative_check("artificial-intelligence")

    message = f"""
🧠 BEAST • MARKET

Macro Score: {macro}/100
AI Narrative Breadth: {ai}

(No portfolio bias)
"""
    bot.send_message(chat_id=MARKET_CHAT_ID, text=message)

if __name__ == "__main__":
    market_report()
