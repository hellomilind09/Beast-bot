import schedule
import time
from telegram import Bot
from config import BOT_TOKEN, PORTFOLIO_CHAT_ID

bot = Bot(BOT_TOKEN)

PORTFOLIO = {
    "VET": 29,
    "OP": 22,
    "AVAX": 19.5,
    "NEAR": 19.5,
    "AR": 10
}

def portfolio_risk():
    layer1_exposure = PORTFOLIO["AVAX"] + PORTFOLIO["NEAR"]

    message = f"""
📊 BEAST • PORTFOLIO

Layer-1 Exposure: {layer1_exposure}%
Enterprise (VET): {PORTFOLIO["VET"]}%

(No market narratives)
"""
    bot.send_message(chat_id=PORTFOLIO_CHAT_ID, text=message)

schedule.every(24).hours.do(portfolio_risk)

while True:
    schedule.run_pending()
    time.sleep(60)
