import os
import requests
from datetime import datetime

# ================== ENV ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")
NARRATIVE_STATE = os.getenv("NARRATIVE_STATE", "")  # optional, from radar

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
    send("⚠️ Portfolio data missing.")
    exit()

portfolio = eval(PORTFOLIO_JSON)
coins = list(portfolio.keys())
prices = fetch_prices(coins)

lines = []
actions = []
weighted_move = 0
volatility = 0

# Narrative bias (simple but effective)
narrative_boost = {
    "ai": ["arweave", "optimism"],
    "infra": ["vechain", "avalanche-2", "near"],
}

positive_narratives = []
if "AI" in NARRATIVE_STATE.upper():
    positive_narratives.append("ai")
if "INFRA" in NARRATIVE_STATE.upper():
    positive_narratives.append("infra")

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

    # ---------- TRIM / HOLD / ADD ----------
    decision = "HOLD"
    reason = "neutral conditions"

    if chg > 8 and w > 20:
        decision = "TRIM"
        reason = "extended move + high weight"

    elif chg < -5 and w < 20:
        decision = "ADD"
        reason = "pullback within controlled exposure"

    for n in positive_narratives:
        if c in narrative_boost[n] and decision != "TRIM":
            decision = "ADD"
            reason = "supported by active narrative"

    actions.append(f"{sym}: <b>{decision}</b> ({reason})")
    lines.append(f"• {sym:<5} | {w:>4.1f}% | ${price:.2f} | {chg:+.2f}%")

# ================== HORIZON INTELLIGENCE ==================
if weighted_move > 2:
    short_term = "Risk-on acceptable → momentum supportive"
elif weighted_move < -2:
    short_term = "Drawdown risk → protect capital"
else:
    short_term = "Range-bound → avoid forcing trades"

if volatility > 6:
    mid_term = "Volatility expanding → rebalance winners"
elif volatility < 3:
    mid_term = "Compression → prepare for breakout"
else:
    mid_term = "Healthy rotational environment"

infra_weight = sum(
    portfolio.get(c, 0)
    for c in ["vechain", "optimism", "avalanche-2", "near"]
)

if infra_weight > 70:
    long_term = "Infra-heavy → diversify across narratives"
else:
    long_term = "Long-cycle exposure balanced"

# ================== MESSAGE ==================
msg = f"""
📊 <b>PORTFOLIO INTELLIGENCE</b>
🕒 {datetime.utcnow().strftime('%d %b %Y | %H:%M UTC')}

<b>Holdings</b>
{chr(10).join(lines)}

<b>Portfolio Pulse</b>
• Weighted 24h move: {weighted_move:+.2f}%
• Volatility score: {volatility:.2f}

<b>📌 TRIM / HOLD / ADD</b>
{chr(10).join(actions)}

<b>⏱ Short Term</b>
{short_term}

<b>📆 Mid Term</b>
{mid_term}

<b>🕰 Long Term</b>
{long_term}
"""

send(msg.strip())
