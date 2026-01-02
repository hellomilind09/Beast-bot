import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

BASE_URL = "https://api.telegram.org/bot" + BOT_TOKEN


# -----------------------------
# TELEGRAM
# -----------------------------
def send_message(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": MARKET_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=10)


# -----------------------------
# MACRO SCORE (simple, stable)
# -----------------------------
def macro_score():
    # Safe placeholder macro logic (you can improve later)
    btc_dominance = 50
    rates_pressure = True

    score = 50
    if btc_dominance > 55:
        score -= 10
    if rates_pressure:
        score -= 5

    return max(0, min(score, 100))


def risk_regime(score):
    if score >= 65:
        return "Risk-On"
    elif score >= 45:
        return "Neutral"
    else:
        return "Risk-Off"


# -----------------------------
# COINGECKO DATA (SAFE)
# -----------------------------
def fetch_category(category):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "category": category,
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "price_change_percentage": "7d"
            },
            timeout=15
        )
        data = r.json()
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


# -----------------------------
# NARRATIVE ANALYSIS
# -----------------------------
def analyze_narrative(name, category):
    coins = fetch_category(category)
    if not coins:
        return {
            "status": "Data error",
            "leaders": [],
            "laggards": [],
            "explanation": "CoinGecko data unavailable"
        }

    leaders = []
    laggards = []

    for c in coins:
        if not isinstance(c, dict):
            continue

        change = c.get("price_change_percentage_7d") or 0

        if change >= 40:
            leaders.append((c["symbol"].upper(), round(change, 1)))
        elif change <= 5:
            laggards.append(c["symbol"].upper())

    if len(leaders) >= 2:
        status = "HOT"
    elif len(leaders) == 1:
        status = "WARM"
    else:
        status = "WEAK"

    explanation = narrative_reason(name)

    return {
        "status": status,
        "leaders": leaders[:3],
        "laggards": laggards[:4],
        "explanation": explanation
    }


def narrative_reason(name):
    reasons = {
        "Privacy": "Regulatory pressure, censorship resistance demand, short squeezes",
        "AI / Compute": "GPU scarcity, AI infra spend, compute monetization",
        "Layer 2s": "Ethereum scaling demand, rollup adoption",
        "RWA": "TradFi yield migration, tokenized treasuries",
        "Gaming": "User growth cycles, infra maturity",
        "DePIN": "Real-world infra monetization, AI hardware demand"
    }
    return reasons.get(name, "Speculative rotation")


# -----------------------------
# MARKET REPORT
# -----------------------------
def market_report():
    score = macro_score()
    regime = risk_regime(score)
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    narratives = {
        "Privacy": "privacy-coins",
        "AI / Compute": "artificial-intelligence",
        "Layer 2s": "layer-2",
        "RWA": "real-world-assets-rwa",
        "Gaming": "gaming",
        "DePIN": "decentralized-infrastructure"
    }

    message = f"""🧠 *MARKET SNAPSHOT*
⏰ {now}

*Risk Regime:* {regime}
*Macro Score:* {score}/100

*NARRATIVE RADAR*
"""

    for name, category in narratives.items():
        info = analyze_narrative(name, category)

        if info["status"] == "HOT":
            emoji = "🔥"
        elif info["status"] == "WARM":
            emoji = "🟡"
        elif info["status"] == "WEAK":
            emoji = "🔴"
        else:
            emoji = "⚠️"

        message += f"\n{emoji} *{name}*: {info['status']}"

        if info["leaders"]:
            leaders = ", ".join([f"{s} ({p}%)" for s, p in info["leaders"]])
            message += f"\n• Leaders: {leaders}"

        if info["laggards"]:
            message += f"\n• Laggards: {', '.join(info['laggards'])}"

        message += f"\n• Why: {info['explanation']}\n"

    send_message(message)


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    market_report()        emoji = "🟢" if v == "Strong" else "🟡" if v == "Moderate" else "🔴"
        msg += f"\n{emoji} {k}: {v}"

    send(msg)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    market_report()
