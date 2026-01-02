import os
import requests
import time
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# -------------------------
# CONFIG
# -------------------------
VS_CURRENCY = "usd"
TOP_N = 50
PRICE_MOVE_STRONG = 15
VOLUME_SURGE = 1.5

# Narrative baskets (editable)
NARRATIVES = {
    "AI / Compute": ["render-token", "fetch-ai", "bittensor"],
    "Privacy": ["zcash", "monero", "secret"],
    "Layer 2s": ["arbitrum", "optimism", "polygon"],
    "DePIN / Infra": ["helium", "iotex"],
    "Gaming": ["immutable-x", "gala"],
    "RWA / Tokenization": ["ondo-finance", "chainlink"]
}

# -------------------------
# HELPERS
# -------------------------
def cg_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": TOP_N,
        "page": 1,
        "price_change_percentage": "24h,7d"
    }
    return requests.get(url, params=params, timeout=20).json()

def btc_dominance(market):
    btc = next((c for c in market if c["id"] == "bitcoin"), None)
    total = sum(c.get("market_cap", 0) or 0 for c in market)
    if not btc or total == 0:
        return None
    return round((btc["market_cap"] / total) * 100, 2)

def send(msg):
    requests.post(TG_URL, data={
        "chat_id": MARKET_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

# -------------------------
# CORE LOGIC
# -------------------------
def narrative_check(market, ids):
    coins = [c for c in market if c["id"] in ids]

    if not coins:
        return "Data error", None, None

    movers = []
    for c in coins:
        try:
            if (c.get("price_change_percentage_7d_in_currency") or 0) > PRICE_MOVE_STRONG:
                movers.append(c)
        except:
            pass

    avg_7d = sum((c.get("price_change_percentage_7d_in_currency") or 0) for c in coins) / len(coins)
    avg_vol = sum((c.get("total_volume") or 0) for c in coins) / len(coins)

    if avg_7d > 10:
        strength = "Strong"
    elif avg_7d > 3:
        strength = "Moderate"
    else:
        strength = "Weak"

    return strength, avg_7d, avg_vol

def velocity_label(change):
    if change > 20:
        return "🔥 Accelerating"
    elif change > 8:
        return "⬆ Rising"
    elif change > 0:
        return "➖ Flat"
    else:
        return "⬇ Cooling"

def macro_score(btc_dom, btc_24h):
    score = 50
    if btc_24h < -2:
        score += 10
    if btc_dom and btc_dom > 52:
        score -= 10
    return max(0, min(100, score))

# -------------------------
# REPORT
# -------------------------
def market_report():
    market = cg_markets()
    now = datetime.now(timezone.utc).strftime("%d %b %Y | %H:%M UTC")

    btc = next(c for c in market if c["id"] == "bitcoin")
    btc_dom = btc_dominance(market)
    btc_24h = btc.get("price_change_percentage_24h") or 0

    score = macro_score(btc_dom, btc_24h)

    if score >= 65:
        regime = "Risk-On"
    elif score <= 35:
        regime = "Risk-Off"
    else:
        regime = "Neutral"

    msg = f"""
<b>🧠 MARKET SNAPSHOT</b>
🕒 {now}

<b>Risk Regime:</b> {regime}
<b>Macro Score:</b> {score}/100

<b>BTC 24h:</b> {btc_24h:.2f}%
<b>BTC Dominance:</b> {btc_dom}%
"""

    msg += "\n<b>Narratives</b>\n"

    strengths = {}

    for name, ids in NARRATIVES.items():
        v, avg_7d, avg_vol = narrative_check(market, ids)
        strengths[name] = avg_7d or 0

        if v == "Strong":
            emoji = "🟢"
        elif v == "Moderate":
            emoji = "🟡"
        else:
            emoji = "🔴"

        vel = velocity_label(avg_7d or 0)

        msg += f"{emoji} <b>{name}</b>: {v} ({vel})\n"

    # -------------------------
    # ROTATION DETECTION
    # -------------------------
    top = max(strengths, key=strengths.get)
    bottom = min(strengths, key=strengths.get)

    if strengths[top] - strengths[bottom] > 15:
        msg += f"\n🔁 <b>Rotation:</b> {bottom} ➜ {top}\n"

    # -------------------------
    # BTC CONFLICT
    # -------------------------
    if btc_24h > 2 and any(v > 8 for v in strengths.values()):
        msg += "\n⚠️ <b>BTC dominance conflict</b> — alts running with BTC up\n"

    send(msg.strip())

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    market_report()
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
