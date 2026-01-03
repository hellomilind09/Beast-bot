import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ---------- helpers ----------

def send(msg):
    requests.post(TG_URL, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, timeout=10)

def fetch_prices(coins):
    ids = ",".join(coins)
    url = (
        "https://min-api.cryptocompare.com/data/pricemultifull"
        f"?fsyms={','.join([c.upper() for c in coins])}&tsyms=USD"
    )
    r = requests.get(url, timeout=10).json()
    return r.get("RAW", {})

# ---------- main ----------

if not PORTFOLIO_JSON:
    send("⚠️ Portfolio data missing.")
    exit()

portfolio = eval(PORTFOLIO_JSON)
coins = list(portfolio.keys())
prices = fetch_prices(coins)

lines = []
weighted_move = 0
volatility_score = 0

for c, w in portfolio.items():
    sym = c.upper()
    try:
        data = prices[sym]["USD"]
        price = data["PRICE"]
        chg = data["CHANGEPCT24HOUR"]
        weighted_move += chg * (w / 100)
        volatility_score += abs(chg) * (w / 100)
        lines.append(f"• {sym:<5} | {w:>4.1f}% | ${price:.2f} | {chg:+.2f}%")
    except:
        lines.append(f"• {sym:<5} | data unavailable")

# ---------- intelligence layers ----------

if weighted_move > 2:
    short_term = "Momentum strong → risk-on bias acceptable"
elif weighted_move < -2:
    short_term = "Drawdown pressure → protect downside"
else:
    short_term = "Range-bound → patience favored"

if volatility_score > 6:
    mid_term = "Volatility expanding → reduce overweight positions"
elif volatility_score < 3:
    mid_term = "Volatility compressed → breakout risk building"
else:
    mid_term = "Healthy rotation environment"

if portfolio.get("vechain", 0) > 25:
    long_term = "High single-theme exposure → diversification advised"
else:
    long_term = "Balanced long-cycle exposure maintained"

# ---------- message ----------

msg = f"""
📊 <b>PORTFOLIO INTELLIGENCE</b>
🕒 {datetime.utcnow().strftime('%d %b %Y | %H:%M UTC')}

<b>Holdings</b>
{chr(10).join(lines)}

<b>Portfolio Pulse</b>
• Weighted 24h move: {weighted_move:+.2f}%
• Volatility score: {volatility_score:.2f}

<b>⏱ Short Term</b>
{short_term}

<b>📆 Mid Term</b>
{mid_term}

<b>🕰 Long Term</b>
{long_term}
"""

send(msg.strip())
