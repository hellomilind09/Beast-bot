import os
import requests
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

COINGECKO = "https://api.coingecko.com/api/v3"

HEADERS = {"accept": "application/json"}

# Narrative buckets (used only for grouping, NOT filtering)
NARRATIVES = {
    "AI / Compute": ["render-token", "fetch-ai", "akash-network"],
    "Layer 2s": ["arbitrum", "optimism", "polygon"],
    "Gaming": ["immutable-x", "gala", "sandbox"],
    "Privacy": ["zcash", "monero"],
    "Infra": ["chainlink", "filecoin"],
    "Memes": ["dogecoin", "pepe"]
}

# =========================
# HELPERS
# =========================

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": MARKET_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=20)


def get_global():
    r = requests.get(f"{COINGECKO}/global", headers=HEADERS, timeout=20)
    return r.json()["data"]


def get_markets(ids):
    if not ids:
        return []
    r = requests.get(
        f"{COINGECKO}/coins/markets",
        headers=HEADERS,
        params={
            "vs_currency": "usd",
            "ids": ",".join(ids),
            "price_change_percentage": "7d",
        },
        timeout=20
    )
    return r.json()


# =========================
# ANALYSIS LOGIC
# =========================

def macro_analysis(global_data):
    btc_d = global_data["market_cap_percentage"]["btc"]
    eth_d = global_data["market_cap_percentage"]["eth"]

    if btc_d > 55:
        regime = "Risk-Off"
        score = 35
    elif btc_d > 48:
        regime = "Neutral"
        score = 50
    else:
        regime = "Risk-On"
        score = 70

    explanation = (
        "Capital concentrated in BTC. Alt rallies fragile."
        if regime == "Risk-Off"
        else "Balanced conditions. Selective opportunities."
        if regime == "Neutral"
        else "Broad alt participation likely."
    )

    return btc_d, eth_d, regime, score, explanation


def analyze_narrative(name, ids):
    coins = get_markets(ids)
    movers = []
    avg_move = 0

    for c in coins:
        pct = c.get("price_change_percentage_7d_in_currency")
        if pct is None:
            continue
        avg_move += pct
        if pct >= 30:
            movers.append((c["symbol"].upper(), pct))

    count = len(coins)
    avg = avg_move / count if count else 0

    if avg > 20:
        strength = "Strong"
    elif avg > 8:
        strength = "Moderate"
    else:
        strength = "Weak"

    return strength, avg, movers


def detect_anomalies():
    # Top 250 coins scan for extreme moves
    r = requests.get(
        f"{COINGECKO}/coins/markets",
        headers=HEADERS,
        params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "price_change_percentage": "7d",
        },
        timeout=20
    )

    anomalies = []
    for c in r.json():
        pct = c.get("price_change_percentage_7d_in_currency")
        if pct and pct >= 60:
            anomalies.append((c["symbol"].upper(), pct))

    return anomalies


# =========================
# REPORT
# =========================

def market_report():
    global_data = get_global()
    btc_d, eth_d, regime, score, macro_text = macro_analysis(global_data)

    now = datetime.now(timezone.utc).strftime("%d %b %Y | %H:%M UTC")

    message = []
    message.append("🧠 *MARKET SNAPSHOT*")
    message.append(f"🕒 {now}")
    message.append("")
    message.append("*MACRO OVERVIEW*")
    message.append(f"• BTC Dominance: {btc_d:.2f}%")
    message.append(f"• ETH Dominance: {eth_d:.2f}%")
    message.append(f"• Regime: {regime}")
    message.append(f"• Macro Score: {score}/100")
    message.append(f"_Interpretation_: {macro_text}")
    message.append("")

    message.append("*NARRATIVE HEALTH*")
    active = False

    for name, ids in NARRATIVES.items():
        strength, avg, movers = analyze_narrative(name, ids)

        if strength != "Weak":
            active = True
            message.append(f"• {name}: *{strength}* ({avg:.1f}% avg)")

            for m in movers:
                message.append(f"   ↳ {m[0]} +{m[1]:.1f}%")

    if not active:
        message.append("No strong narrative momentum right now.")

    message.append("")

    anomalies = detect_anomalies()
    if anomalies:
        message.append("*SINGLE-COIN ANOMALIES ⚠️*")
        for a in anomalies[:5]:
            message.append(f"• {a[0]} +{a[1]:.1f}% (7D)")
        message.append("")

    if btc_d > 55:
        message.append("⚠️ *BTC Dominance High* — alt moves likely unstable")

    send_telegram("\n".join(message))


# =========================
# ENTRY
# =========================

if __name__ == "__main__":
    market_report()
