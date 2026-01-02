import os
import requests
from datetime import datetime

# ================= CONFIG =================

BOT_TOKEN = os.environ["BOT_TOKEN"]
PORTFOLIO_CHAT_ID = os.environ["PORTFOLIO_CHAT_ID"]

PORTFOLIO_COINS = os.environ.get("PORTFOLIO_COINS", "")
COINS = [c.strip().upper() for c in PORTFOLIO_COINS.split(",") if c.strip()]

WEIGHTS_RAW = os.environ.get("PORTFOLIO_WEIGHTS", "")
WEIGHTS = {}
for pair in WEIGHTS_RAW.split(","):
    if ":" in pair:
        k, v = pair.split(":")
        WEIGHTS[k.strip().upper()] = float(v)

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
CG = "https://api.coingecko.com/api/v3"

# 🔑 SYMBOL → COINGECKO ID MAP (CRITICAL)
COIN_ID_MAP = {
    "VET": "vechain",
    "OP": "optimism",
    "AVAX": "avalanche-2",
    "NEAR": "near",
    "AR": "arweave",
    "MX": "mx-token"
}

# Narrative mapping
NARRATIVES = {
    "VET": "Enterprise / Supply Chain",
    "OP": "Layer 2s",
    "AVAX": "Layer 1 / Infra",
    "NEAR": "Layer 1 / AI-adjacent",
    "AR": "Data / Storage",
    "MX": "Exchange Token"
}

# ================= TELEGRAM =================

def send(msg):
    requests.post(
        TG_URL,
        json={
            "chat_id": PORTFOLIO_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )

# ================= DATA =================

def get_market_data():
    ids = [COIN_ID_MAP[c] for c in COINS if c in COIN_ID_MAP]
    if not ids:
        return []

    try:
        r = requests.get(
            f"{CG}/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(ids),
                "price_change_percentage": "24h,7d"
            },
            timeout=20
        )
        data = r.json()
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return []

# ================= LOGIC =================

def classify(p7d):
    if p7d is None:
        return "No Data"
    if p7d >= 15:
        return "Contributor"
    if p7d <= -15:
        return "Drag"
    return "Neutral"

# ================= REPORT =================

def portfolio_report():
    data = get_market_data()
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    msg = []
    msg.append("<b>📊 PORTFOLIO INTELLIGENCE</b>")
    msg.append(f"🕒 {now}")
    msg.append("")

    if not data:
        msg.append("⚠️ Portfolio data unavailable.")
        msg.append("Check Coin IDs or API limits.")
        send("\n".join(msg))
        return

    contributors = []
    drags = []
    narrative_exposure = {}

    for c in data:
        symbol = c.get("symbol", "").upper()
        p24 = c.get("price_change_percentage_24h")
        p7d = c.get("price_change_percentage_7d_in_currency")

        weight = WEIGHTS.get(symbol, 0)
        status = classify(p7d)

        msg.append(
            f"<b>{symbol}</b> ({weight}%) | "
            f"24h: {p24:.1f}% | 7d: {p7d:.1f}% → {status}"
        )

        if status == "Contributor":
            contributors.append(symbol)
        elif status == "Drag":
            drags.append(symbol)

        narrative = NARRATIVES.get(symbol, "Other")
        narrative_exposure[narrative] = narrative_exposure.get(narrative, 0) + weight

    # ===== SUMMARY =====
    msg.append("")
    msg.append("<b>SUMMARY</b>")

    if contributors:
        msg.append("🟢 Contributors: " + ", ".join(contributors))
    if drags:
        msg.append("🔴 Drags: " + ", ".join(drags))
    if not contributors and not drags:
        msg.append("Portfolio broadly neutral.")

    # ===== RISK =====
    msg.append("")
    msg.append("<b>RISK CHECK</b>")

    high_exposure = [k for k, v in WEIGHTS.items() if v >= 25]
    if high_exposure:
        msg.append("⚠️ High single-coin exposure: " + ", ".join(high_exposure))

    if len(drags) >= max(2, len(COINS)//2):
        msg.append("⚠️ Multiple holdings dragging simultaneously")

    # ===== NARRATIVES =====
    msg.append("")
    msg.append("<b>NARRATIVE EXPOSURE</b>")
    for n, v in narrative_exposure.items():
        msg.append(f"• {n}: {round(v,1)}%")

    dominant = [n for n, v in narrative_exposure.items() if v >= 50]
    if dominant:
        msg.append("⚠️ Overexposed to narrative: " + ", ".join(dominant))

    send("\n".join(msg))

# ================= RUN =================

if __name__ == "__main__":
    portfolio_report()
