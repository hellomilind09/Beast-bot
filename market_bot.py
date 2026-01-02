import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# -------------------------------
# SAFE TELEGRAM SEND
# -------------------------------
def send(msg):
    requests.post(
        TG_URL,
        data={
            "chat_id": MARKET_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        },
        timeout=10
    )


# -------------------------------
# MACRO SCORE (UNCHANGED LOGIC)
# -------------------------------
def macro_score():
    score = 50

    try:
        btc = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=10
        ).json()

        btc_change = btc["bitcoin"]["usd_24h_change"]

        if btc_change > 2:
            score += 10
        elif btc_change < -2:
            score -= 10

    except Exception:
        pass

    return max(0, min(100, score))


# -------------------------------
# FIXED NARRATIVE CHECK (SAFE)
# -------------------------------
def narrative_check(category):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "category": category,
                "price_change_percentage": "7d"
            },
            timeout=10
        )

        data = r.json()

        # 🔒 SAFETY CHECK (THIS IS THE FIX)
        if not isinstance(data, list):
            return "Data error"

        movers = []
        for c in data:
            if not isinstance(c, dict):
                continue

            if c.get("price_change_percentage_7d", 0) > 15:
                movers.append(c)

        if len(movers) >= 3:
            return "Strong"
        elif len(movers) == 2:
            return "Moderate"
        else:
            return "Weak"

    except Exception:
        return "Unavailable"


# -------------------------------
# MARKET REPORT
# -------------------------------
def market_report():
    score = macro_score()

    regime = (
        "Risk-On" if score >= 65 else
        "Risk-Off" if score <= 35 else
        "Neutral"
    )

    narratives = {
        "AI / Compute": narrative_check("artificial-intelligence"),
        "RWA / Tokenization": narrative_check("real-world-assets"),
        "Layer 2s": narrative_check("layer-2"),
        "DePIN / Infra": narrative_check("depin"),
        "Gaming": narrative_check("gaming")
    }

    msg = f"""🧠 <b>MARKET SNAPSHOT</b>
🕒 {datetime.utcnow().strftime('%d %b %Y | %H:%M UTC')}

<b>Risk Regime:</b> {regime}
<b>Macro Score:</b> {score}/100

<b>Narratives</b>"""

    for k, v in narratives.items():
        emoji = "🟢" if v == "Strong" else "🟡" if v == "Moderate" else "🔴"
        msg += f"\n{emoji} {k}: {v}"

    send(msg)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    market_report()
