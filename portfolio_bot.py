import schedule, time
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
    l1_exposure = PORTFOLIO["AVAX"] + PORTFOLIO["NEAR"]
    msg = f"""
📊 PORTFOLIO RISK

Layer-1 Exposure: {l1_exposure}%
Enterprise Exposure: {PORTFOLIO["VET"]}%

(No narrative input)
"""
    bot.send_message(chat_id=PORTFOLIO_CHAT_ID, text=msg)

schedule.every(24).hours.do(portfolio_risk)

while True:
    schedule.run_pending()
    time.sleep(60)
