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
def get_top_markets():
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

# ===================== LOGIC =====================
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
    narrative_hits = {}

    for c in coins:
        if not isinstance(c, dict):
            continue

        symbol = c.get("symbol", "").upper()
        p24 = c.get("price_change_percentage_24h")
        p7d = c.get("price_change_percentage_7d_in_currency")

        if not symbol:
            continue

        if in_cooldown(symbol, state):
            continue

        triggered = False
        reason = ""

        if p24 is not None and p24 >= 25:
            triggered = True
            reason = f"+{p24:.1f}% in 24h"
        elif p7d is not None and p7d >= 60:
            triggered = True
            reason = f"+{p7d:.1f}% in 7D"

        if not triggered:
            continue

        tag = "[HELD]" if symbol in PORTFOLIO else "[WATCH]"
        alerts.append(f"⚠️ <b>{symbol}</b> {reason} {tag}")

        mark_alerted(symbol, state)

        cat = c.get("category")
        if cat:
            narrative_hits.setdefault(cat, []).append(symbol)

    # Narrative ignition detection
    narrative_alerts = []
    for cat, syms in narrative_hits.items():
        if len(syms) >= 3:
            narrative_alerts.append(
                f"🔥 <b>Narrative ignition</b>: {cat} ({', '.join(syms[:4])})"
            )

    return alerts, narrative_alerts

# ===================== RUN =====================
def action_report():
    coins = get_top_markets()
    state = load_state()

    alerts, narrative_alerts = detect_actions(coins, state)

    if not alerts and not narrative_alerts:
        return  # silence is intentional

    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    msg = "<b>🚨 ACTION ALERT</b>\n"
    msg += f"🕒 {now}\n\n"

    for a in alerts:
        msg += a + "\n"

    if narrative_alerts:
        msg += "\n"
        for n in narrative_alerts:
            msg += n + "\n"

    send(msg.strip())
    save_state(state)

if __name__ == "__main__":
    action_report()
