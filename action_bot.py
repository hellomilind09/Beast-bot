import os
import json
import requests
from datetime import datetime, timedelta

# ================= CONFIG =================

BOT_TOKEN = os.environ["BOT_TOKEN"]
ACTION_CHAT_ID = os.environ["ACTION_CHAT_ID"]

PORTFOLIO_COINS = os.environ.get("PORTFOLIO_COINS", "")
PORTFOLIO = [c.strip().upper() for c in PORTFOLIO_COINS.split(",") if c.strip()]

PORTFOLIO_WEIGHTS_RAW = os.environ.get("PORTFOLIO_WEIGHTS", "")
PORTFOLIO_WEIGHTS = {}
for pair in PORTFOLIO_WEIGHTS_RAW.split(","):
    if ":" in pair:
        k, v = pair.split(":")
        PORTFOLIO_WEIGHTS[k.strip().upper()] = float(v)

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
STATE_FILE = "action_state.json"
COINGECKO = "https://api.coingecko.com/api/v3"

COOLDOWN_HOURS = 6

# ================= STATE =================

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ================= TELEGRAM =================

def send(msg):
    requests.post(
        TG_URL,
        json={
            "chat_id": ACTION_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )

# ================= DATA =================

def get_markets():
    try:
        r = requests.get(
            f"{COINGECKO}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 250,
                "page": 1,
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

# ================= HELPERS =================

def in_cooldown(symbol, state):
    last = state.get(symbol)
    if not last:
        return False
    return datetime.utcnow() - datetime.fromisoformat(last) < timedelta(hours=COOLDOWN_HOURS)

def mark_alerted(symbol, state):
    state[symbol] = datetime.utcnow().isoformat()

def high_exposure(symbol, threshold=25):
    return PORTFOLIO_WEIGHTS.get(symbol, 0) >= threshold

def impulse_quality(p24):
    if p24 >= 40:
        return "Very fast impulse"
    if p24 >= 25:
        return "Fast expansion"
    return "Gradual move"

# ================= CORE LOGIC =================

def detect_actions(coins, state):
    alerts = []

    for c in coins:
        if not isinstance(c, dict):
            continue

        symbol = c.get("symbol", "").upper()
        if not symbol or in_cooldown(symbol, state):
            continue

        p24 = c.get("price_change_percentage_24h")
        p7d = c.get("price_change_percentage_7d_in_currency")
        vol = c.get("total_volume")
        mc = c.get("market_cap")

        # ---------- SAFETY ----------
        if p24 is None or vol is None or mc is None:
            continue

        # =====================================================
        # 1️⃣ GLOBAL ANOMALY ALERT
        # =====================================================
        if p24 >= 25 or (p7d is not None and p7d >= 60):
            msg = []
            msg.append(f"<b>{symbol}</b> anomaly detected")
            msg.append(f"Move: +{p24:.1f}% (24h)")
            msg.append(f"Impulse: {impulse_quality(p24)}")
            msg.append("Volume: Confirmed" if vol / mc > 0.1 else "Volume: Weak")

            relevance = "🔥 HIGH" if symbol in PORTFOLIO else "⚪ LOW"
            msg.append("")
            msg.append(f"<b>Portfolio Relevance:</b> {relevance}")

            alerts.append("\n".join(msg))
            mark_alerted(symbol, state)
            continue

        # =====================================================
        # 2️⃣ PORTFOLIO EXPOSURE + WEAKNESS ALERT
        # =====================================================
        if symbol in PORTFOLIO and high_exposure(symbol):
            weak_24h = p24 <= -8
            weak_7d = p7d is not None and p7d <= -15

            if weak_24h or weak_7d:
                msg = []
                msg.append(f"<b>{symbol}</b> weakness detected")
                if weak_24h:
                    msg.append(f"Move: {p24:.1f}% (24h)")
                else:
                    msg.append(f"Move: {p7d:.1f}% (7d)")
                msg.append(f"Exposure: {PORTFOLIO_WEIGHTS[symbol]}% (High)")
                msg.append("")
                msg.append("Context:")
                msg.append("High-conviction position showing abnormal weakness.")
                msg.append("Not a market-wide signal.")
                msg.append("")
                msg.append("Action:")
                msg.append("Risk awareness required (no forced action)")

                alerts.append("\n".join(msg))
                mark_alerted(symbol, state)

    return alerts

# ================= RUN =================

def action_report():
    coins = get_markets()
    state = load_state()

    alerts = detect_actions(coins, state)
    if not alerts:
        return

    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")
    msg = "<b>🚨 ACTION ALERT</b>\n"
    msg += f"🕒 {now}\n\n"
    msg += "\n\n".join(alerts)

    send(msg)
    save_state(state)

if __name__ == "__main__":
    action_report()
