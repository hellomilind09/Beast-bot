import os
import requests
from datetime import datetime

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")
NARRATIVE_STATE = os.getenv("NARRATIVE_STATE", "")  # optional text summary

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ================= TELEGRAM =================
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

# ================= SYMBOL MAP =================
SYMBOL_MAP = {
    "vechain": "VET",
    "optimism": "OP",
    "avalanche-2": "AVAX",
    "near": "NEAR",
    "arweave": "AR",
}

# ================= PRICE ENGINE =================
def fetch_prices(coins):
    prices = {}

    # ---- PRIMARY: CRYPTOCOMPARE ----
    try:
        syms = ",".join(SYMBOL_MAP.get(c, c.upper()) for c in coins)
        url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={syms}&tsyms=USD"
        raw = requests.get(url, timeout=15).json().get("RAW", {})

        for c in coins:
            sym = SYMBOL_MAP.get(c, c.upper())
            if sym in raw:
                prices[c] = {
                    "price": raw[sym]["USD"]["PRICE"],
                    "change": raw[sym]["USD"]["CHANGEPCT24HOUR"],
                }
    except:
        pass

    # ---- FALLBACK: COINGECKO ----
    missing = [c for c in coins if c not in prices]
    if missing:
        try:
            ids = ",".join(missing)
            url = (
                "https://api.coingecko.com/api/v3/simple/price"
                f"?ids={ids}&vs_currencies=usd&include_24hr_change=true"
            )
            data = requests.get(url, timeout=15).json()
            for c in missing:
                if c in data:
                    prices[c] = {
                        "price": data[c]["usd"],
                        "change": data[c]["usd_24h_change"],
                    }
        except:
            pass

    return prices

# ================= SAFETY =================
if not BOT_TOKEN or not CHAT_ID:
    exit()

if not PORTFOLIO_JSON:
    send("⚠️ Portfolio data missing.")
    exit()

portfolio = eval(PORTFOLIO_JSON)
coins = list(portfolio.keys())
prices = fetch_prices(coins)

# ================= METRICS =================
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
    send("⚠️ Price sources unavailable.")
    exit()

# ================= PORTFOLIO POSTURE =================
if weighted_move > 2 and volatility < 4:
    posture = "AGGRESSIVE"
elif weighted_move < -2 or volatility > 7:
    posture = "DEFENSIVE"
elif volatility >= 4:
    posture = "NEUTRAL–DEFENSIVE"
else:
    posture = "NEUTRAL"

# ================= WHY =================
why = []
why.append(f"Portfolio 24h move {weighted_move:+.2f}%")
why.append(f"Volatility score {volatility:.2f}")

infra_weight = sum(
    portfolio.get(c, 0)
    for c in ["vechain", "optimism", "avalanche-2", "near"]
)

if infra_weight > 65:
    why.append("Returns concentrated in infra cluster")

if "AI" in NARRATIVE_STATE.upper():
    why.append("AI narrative supportive")
elif "INFRA" in NARRATIVE_STATE.upper():
    why.append("Infra narrative mixed")
else:
    why.append("No dominant narrative tailwind")

# ================= RISK PRESSURE MAP =================
pressure = []
if portfolio.get("vechain", 0) > 25:
    pressure.append("VET overweight → downside amplifier if infra weakens")

if portfolio.get("optimism", 0) + portfolio.get("avalanche-2", 0) > 35:
    pressure.append("OP + AVAX → correlated risk cluster")

if portfolio.get("arweave", 0) < 15:
    pressure.append("AR provides diversification but limited size")

# ================= ACTION READINESS =================
if posture in ["DEFENSIVE", "NEUTRAL–DEFENSIVE"]:
    readiness = [
        "No immediate action optimal",
        "Prepare to act only on confirmation",
        "Protect capital over chasing returns",
    ]
elif posture == "NEUTRAL":
    readiness = [
        "Prepare to act selectively",
        "Only add risk on narrative + volatility expansion",
    ]
else:
    readiness = [
        "Environment supportive",
        "Prepare to add on pullbacks, not breakouts",
    ]

# ================= MESSAGE =================
msg = f"""
📊 <b>PORTFOLIO INTELLIGENCE</b>
🕒 {datetime.utcnow().strftime('%d %b %Y | %H:%M UTC')}

<b>HOLDINGS</b>
{chr(10).join(lines)}

<b>PORTFOLIO POSTURE</b>
{posture}

<b>WHY</b>
• {' | '.join(why)}

<b>RISK PRESSURE POINTS</b>
• {' | '.join(pressure)}

<b>ACTION READINESS</b>
• {' | '.join(readiness)}
"""

send(msg.strip())
