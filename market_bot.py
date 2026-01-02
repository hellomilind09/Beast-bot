import os
import requests
from datetime import datetime

# ================= ENV =================
BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
CG = "https://api.coingecko.com/api/v3"


# ================= TELEGRAM =================
def send_message(text):
    payload = {
        "chat_id": MARKET_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(TG_URL, data=payload, timeout=20)


# ================= DATA =================
def get_global():
    r = requests.get(f"{CG}/global", timeout=20)
    return r.json()["data"]


def get_categories():
    r = requests.get(f"{CG}/coins/categories", timeout=20)
    return r.json()


def get_category_coins(cat_id):
    params = {
        "vs_currency": "usd",
        "category": cat_id,
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "price_change_percentage": "7d"
    }
    r = requests.get(f"{CG}/coins/markets", params=params, timeout=20)
    return r.json()


# ================= MACRO =================
def macro_view():
    g = get_global()
    btc_d = round(g["market_cap_percentage"].get("btc", 0), 2)
    eth_d = round(g["market_cap_percentage"].get("eth", 0), 2)

    if btc_d > 52:
        regime = "Risk-Off"
        score = 35
    elif btc_d < 48:
        regime = "Risk-On"
        score = 70
    else:
        regime = "Neutral"
        score = 50

    return btc_d, eth_d, regime, score


# ================= NARRATIVE =================
def analyze_category(cat):
    coins = get_category_coins(cat["id"])

    movers = []
    changes = []

    for c in coins:
        # 🔒 HARD GUARD (THIS FIXES YOUR CRASH)
        if not isinstance(c, dict):
            continue

        pct = c.get("price_change_percentage_7d")
        if pct is None:
            continue

        changes.append(pct)

        if pct >= 15:
            symbol = c.get("symbol", "").upper()
            movers.append(f"{symbol} +{round(pct,1)}%")

    if not changes:
        return None

    avg = sum(changes) / len(changes)

    if avg >= 15:
        strength = "🟢 HOT"
    elif avg >= 7:
        strength = "🟡 WARM"
    else:
        strength = "🔴 COOL"

    return {
        "name": cat.get("name", "Unknown"),
        "avg": round(avg, 1),
        "strength": strength,
        "movers": movers[:4]
    }


# ================= REPORT =================
def market_report():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    btc_d, eth_d, regime, score = macro_view()
    categories = get_categories()

    lines = []
    lines.append("🧠 <b>MARKET SNAPSHOT</b>")
    lines.append(f"🕒 {now}")
    lines.append("")
    lines.append("<b>MACRO</b>")
    lines.append(f"• BTC Dominance: {btc_d}%")
    lines.append(f"• ETH Dominance: {eth_d}%")
    lines.append(f"• Regime: {regime}")
    lines.append(f"• Macro Score: {score}/100")
    lines.append("")
    lines.append("<b>ACTIVE NARRATIVES</b>")

    shown = 0

    for cat in categories:
        info = analyze_category(cat)
        if not info:
            continue
        if info["strength"] == "🔴 COOL":
            continue

        lines.append("")
        lines.append(
            f'{info["strength"]} <b>{info["name"]}</b> (avg {info["avg"]}%)'
        )

        for m in info["movers"]:
            lines.append(f"• {m}")

        shown += 1
        if shown >= 8:
            break

    if shown == 0:
        lines.append("")
        lines.append("No strong narrative momentum right now.")

    send_message("\n".join(lines))


# ================= RUN =================
if __name__ == "__main__":
    market_report()
