import os
import requests
from datetime import datetime

# ================== ENV ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ================== TELEGRAM ==================
def send(msg):
    requests.post(
        TG_URL,
        json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )

# ================== PRICE ENGINE ==================
SYMBOL_MAP = {
    "vechain": "VET",
    "optimism": "OP",
    "avalanche-2": "AVAX",
    "near": "NEAR",
    "arweave": "AR",
}

def fetch_prices(coins):
    prices = {}

    # ---------- PRIMARY: CRYPTOCOMPARE ----------
    try:
        syms = ",".join(SYMBOL_MAP.get(c, c.upper()) for c in coins)
        url = (
            "https://min-api.cryptocompare.com/data/pricemultifull"
            f"?fsyms={syms}&tsyms=USD"
        )
        r = requests.get(url, timeout=15).json()
        raw = r.get("RAW", {})

        for c in coins:
            sym = SYMBOL_MAP.get(c, c.upper())
            if sym in raw:
                prices[c] = {
                    "price": raw[sym]["USD"]["PRICE"],
                    "change": raw[sym]["USD"]["CHANGEPCT24HOUR"],
                }
    except:
        pass

    # ---------- FALLBACK: COINGECKO ----------
    missing = [c for c in coins if c not in prices]

    if missing:
        try:
            ids = ",".join(missing)
            url = (
                "https://api.coingecko.com/api/v3/simple/price"
                f"?ids={ids}&vs_currencies=usd&include_24hr_change=true"
            )
            r = requests.get(url, timeout=15).json()

            for c in missing:
                if c in r:
                    prices[c] = {
                        "price": r[c]["usd"],
                        "change": r[c]["usd_24h_change"],
                    }
        except:
            pass

    return prices

# ================== MAIN ==================
if not BOT_TOKEN or not CHAT_ID:
    exit()

if not PORTFOLIO_JSON:
    send("⚠️ Portfolio data missing.\nCheck PORTFOLIO_JSON variable.")
    exit()

try:
    portfolio = eval(PORTFOLIO_JSON)
except:
    send("⚠️ Portfolio JSON invalid.")
    exit()

coins = list(portfolio.keys())
prices = fetch_prices(coins)

lines = []
weighted_move = 0.0
volatility = 0.0
valid_weight = 0.0

for c, w in portfolio.items():
    sym = SYMBOL_MAP.get(c, c.upper())
    data = prices.get(c)

    if not data:
        lines.append(f"• {sym:<5} | {w:>4.1f}% | data unavailable")
        continue

    price = data["price"]
    chg = data["change"]

    weighted_move += chg * (w / 100)
    volatility += abs(chg) * (w / 100)
    valid_weight += w

    lines.append(f"• {sym:<5} | {w:>4.1f}% | ${price:.2f} | {chg:+.2f}%")

if valid_weight == 0:
    send("⚠️ Price sources unavailable (CryptoCompare + CoinGecko failed).")
    exit()

# ================== INTELLIGENCE ==================
# Short term
if weighted_move > 2:
    short_term = "Momentum strong → risk-on acceptable"
elif weighted_move < -2:
    short_term = "Downside pressure → capital protection"
else:
    short_term = "Chop / range → patience favored"

# Mid term
if volatility > 6:
    mid_term = "Volatility expanding → trim overweights"
elif volatility < 3:
    mid_term = "Volatility compressed → breakout risk building"
else:
    mid_term = "Healthy rotational environment"

# Long term
infra_weight = sum(
    portfolio.get(c, 0)
    for c in ["vechain", "optimism", "avalanche-2", "near"]
)

if infra_weight > 70:
    long_term = "High infra concentration → diversification advised"
else:
    long_term = "Long-term exposure balanced"

# ================== MESSAGE ==================
msg = f"""
📊 <b>PORTFOLIO INTELLIGENCE</b>
🕒 {datetime.utcnow().strftime('%d %b %Y | %H:%M UTC')}

<b>Holdings</b>
{chr(10).join(lines)}

<b>Portfolio Pulse</b>
• Weighted 24h move: {weighted_move:+.2f}%
• Volatility score: {volatility:.2f}

<b>⏱ Short Term</b>
{short_term}

<b>📆 Mid Term</b>
{mid_term}

<b>🕰 Long Term</b>
{long_term}
"""

send(msg.strip())
