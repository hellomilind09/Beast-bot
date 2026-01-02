import os
import schedule
import time
from telegram import Bot
from market_bot import macro_score, narrative_check
from portfolio_bot import PORTFOLIO

BOT_TOKEN = os.environ["BOT_TOKEN"]
ACTION_CHAT_ID = os.environ["ACTION_CHAT_ID"]

bot = Bot(BOT_TOKEN)

def decision_engine():
    macro = macro_score()
    ai = narrative_check("artificial-intelligence")
    layer1_exposure = PORTFOLIO["AVAX"] + PORTFOLIO["NEAR"]

    if macro >= 70 and ai >= 3 and layer1_exposure > 40:
        message = """
🚨 BEAST • ACTION

Risk-on confirmed
AI narrative forming
Layer-1 exposure high

🎯 ACTION:
Rotate PARTIAL Layer-1 → AI
"""
        bot.send_message(chat_id=ACTION_CHAT_ID, text=message)

schedule.every(6).hours.do(decision_engine)

while True:
    schedule.run_pending()
    time.sleep(60)
