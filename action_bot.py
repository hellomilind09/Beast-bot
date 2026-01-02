import os
import json
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
ACTION_CHAT_ID = os.environ["ACTION_CHAT_ID"]

PORTFOLIO = os.environ.get("PORTFOLIO_COINS", "")
PORTFOLIO = [c.strip().upper() for c in PORTFOLIO.split(",") if c.strip()]

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
STATE_FILE = "action_state.json"

COINGECKO = "https://api.coingecko.com/api/v3"
COOLDOWN_HOURS = 6

# ===================== STATE =====================
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ===================== TELEGRAM =====================
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

# ===================== DATA =====================
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

# ===================== SIGNAL LOGIC =====================
def impulse_quality(p24):
    if p24 >= 40:
        return "Very Fast Impulse"
    if p24 >= 25:
        return "Fast Expansion"
    return "Gradual Move"

def follow_through_risk(p24):
    if p24 >= 45:
        return "Late / Overextended"
    if p24 >= 25:
        return "Mid-Impulse"
    return "Early"

def in_cooldown(symbol, state):
    last = state.get(symbol)
    if not last:
        return False
    last_time = datetime.fromisoformat(last)
    return datetime.utcnow() - last_time < timedelta(hours=COOLDOWN_HOURS)

def mark_alerted(symbol, state):
    state[symbol] = datetime.utcnow().isoformat()

def detect_actions(coins, state):
    alerts = []

    for c in coins:
        if not isinstance(c, dict):
            continue

        symbol = c.get("symbol", "").upper()
        if not symbol:
            continue

        if in_cooldown(symbol, state):
            continue

        p24 = c.get("price_change_percentage_24h")
        p7d = c.get("price_change_percentage_7d_in_currency")
        vol = c.get("total_volume")
        mc = c.get("market_cap")

        if p24 is None or vol is None or mc is None:
            continue

        # Core trigger
        if p24 < 25 and (p7d is None or p7d < 60):
            continue

        vol_ratio = vol / mc if mc > 0 else 0

        impulse = impulse_quality(p24)
        extension = follow_through_risk(p24)

        volume_signal = (
            "Strong Volume Confirmation" if vol_ratio > 0.15
            else "Weak Volume Confirmation"
        )

        tag = "HELD" if symbol in PORTFOLIO else "WATCH"

        msg = []
        msg.append(f"<b>{symbol}</b> anomaly detected")
        msg.append(f"Move: +{p24:.1f}% (24h)")
        msg.append(f"Impulse Quality: {impulse}")
        msg.append(f"Volume Signal: {volume_signal}")
        msg.append(f"Follow-through Risk: {extension}")
        msg.append(f"Portfolio: [{tag}]")

        alerts.append("\n".join(msg))
        mark_alerted(symbol, state)

    return alerts

# ===================== RUN =====================
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
