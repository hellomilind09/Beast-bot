import os
import json
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
ACTION_CHAT_ID = os.environ["ACTION_CHAT_ID"]

PORTFOLIO_COINS = os.environ.get("PORTFOLIO_COINS", "")
PORTFOLIO = [c.strip().upper() for c in PORTFOLIO_COINS.split(",") if c.strip()]

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

# ================= LOGIC =================
def in_cooldown(symbol, state):
    last = state.get(symbol)
    if not last:
        return False
    return datetime.utcnow() - datetime.fromisoformat(last) < timedelta(hours=COOLDOWN_HOURS)

def mark_alerted(symbol, state):
    state[symbol] = datetime.utcnow().isoformat()

def portfolio_relevance(symbol):
    if symbol in PORTFOLIO:
        return "🔥 HIGH", "Direct holding in portfolio"

    # narrative proximity (simple heuristic)
    narrative_links = {
        "AVAX": ["NEAR", "SOL"],
        "NEAR": ["AVAX"],
        "OP": ["ARB"],
        "VET": ["IOTA"],
        "AR": ["FIL"]
    }

    for held in PORTFOLIO:
        if symbol in narrative_links.get(held, []):
            return "🟡 MEDIUM", f"Related to {held} narrative"

    return "⚪ LOW", "No portfolio exposure"

def impulse(p24):
    if p24 >= 40:
        return "Very fast impulse"
    if p24 >= 25:
        return "Fast expansion"
    return "Gradual move"

# ================= ACTION DETECTION =================
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

        if p24 is None or vol is None or mc is None:
            continue

        if p24 < 25 and (p7d is None or p7d < 60):
            continue

        relevance, reason = portfolio_relevance(symbol)

        msg = []
        msg.append(f"<b>{symbol}</b> anomaly detected")
        msg.append(f"Move: +{p24:.1f}% (24h)")
        msg.append(f"Impulse: {impulse(p24)}")
        msg.append("Volume: Confirmed" if vol/mc > 0.1 else "Volume: Weak")
        msg.append("")
        msg.append(f"<b>Portfolio Relevance:</b> {relevance}")
        msg.append(f"Reason: {reason}")

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
