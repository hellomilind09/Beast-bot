import schedule, time
from telegram import Bot
from config import BOT_TOKEN, ACTION_CHAT_ID
from market_bot import macro_score, narrative_check
from portfolio_bot import PORTFOLIO

bot = Bot(BOT_TOKEN)

def decision_engine():
    macro = macro_score()
    ai = narrative_check("artificial-intelligence")
    l1 = PORTFOLIO["AVAX"] + PORTFOLIO["NEAR"]

    if macro >= 70 and ai >= 3 and l1 > 40:
        msg = """
🚨 ACTION ALERT

Risk-on confirmed
AI narrative forming
L1 exposure high

🎯 ACTION:
Rotate PARTIAL L1 → AI
"""
        bot.send_message(chat_id=ACTION_CHAT_ID, text=msg)

schedule.every(6).hours.do(decision_engine)

while True:
    schedule.run_pending()
    time.sleep(60)
