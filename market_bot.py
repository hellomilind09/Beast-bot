import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MARKET_CHAT_ID = os.environ.get("MARKET_CHAT_ID")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# ===================== SAFE TELEGRAM =====================
def send(msg):
    requests.post(TG_URL, json={
        "chat_id": MARKET_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })


# ===================== MACRO =====================
def get_macro():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=20)
        d = r.json()["data"]

        btc_d = d["market_cap_percentage"].get("btc", 0)
        eth_d = d["market_cap_percentage"].get("eth", 0)

        score = 100 - int(btc_d)
        regime = "Risk-On" if score > 60 else "Neutral" if score > 40 else "Risk-Off"

        return btc_d, eth_d, regime, score
    except Exception:
        return 0, 0, "Unknown", 0


# ===================== FALLBACK MARKET DATA =====================
def safe_get_markets(ids):
    if not ids:
        return []

    # ---- CoinGecko ----
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(ids),
                "price_change_percentage": "7d"
            },
            timeout=20
        )
        data = r.json()
        if isinstance(data, list):
            return data
    except Exception:
        pass

    # ---- CryptoCompare fallback ----
    try:
        symbols = ",".join([i.split("-")[0].upper() for i in ids])
        r = requests.get(
            "https://min-api.cryptocompare.com/data/pricemultifull",
            params={"fsyms": symbols, "tsyms": "USD"},
            timeout=20
        )
        raw = r.json().get("RAW", {})
        out = []
        for sym, v in raw.items():
            usd = v.get("USD", {})
            out.append({
                "symbol": sym,
                "price_change_percentage_7d_in_currency": usd.get("CHANGEPCT7DAY", 0)
            })
        return out
    except Exception:
        return []


# ===================== NARRATIVES =====================
NARRATIVES = {
    "AI / Compute": ["render-token", "fetch-ai", "akash-network"],
    "RWA / Tokenization": ["chainlink", "ondo-finance", "polymesh"],
    "Layer 2s": ["arbitrum", "optimism", "polygon"],
    "DePIN / Infra": ["helium", "iotex", "akash-network"],
    "Gaming": ["immutable-x", "gala", "ronin"]
}


def analyze_narrative(name, ids):
    data = safe_get_markets(ids)
    if not data:
        return "No Data", 0, []

    moves = []
    total = 0
    count = 0

    for c in data:
        pct = c.get("price_change_percentage_7d_in_currency")
        if pct is None:
            continue
        total += pct
        count += 1
        if pct >= 20:
            moves.append(f"{c.get('symbol','').upper()} +{pct:.1f}%")

    avg = total / count if count else 0

    if avg >= 15:
        strength = "Strong"
    elif avg >= 5:
        strength = "Moderate"
    else:
        strength = "Weak"

    return strength, avg, moves


# ===================== REPORT =====================
def market_report():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    btc_d, eth_d, regime, score = get_macro()

    msg = f"""
<b>🧠 MARKET SNAPSHOT</b>
🕒 {now}

<b>MACRO</b>
• BTC Dominance: {btc_d:.2f}%
• ETH Dominance: {eth_d:.2f}%
• Regime: {regime}
• Macro Score: {score}/100

<b>ACTIVE NARRATIVES</b>
"""

    any_active = False

    for name, ids in NARRATIVES.items():
        strength, avg, movers = analyze_narrative(name, ids)

        emoji = "🟢" if strength == "Strong" else "🟡" if strength == "Moderate" else "🔴"

        msg += f"\n{emoji} <b>{name}</b>: {strength} ({avg:.1f}%)"

        if movers:
            any_active = True
            for m in movers:
                msg += f"\n   • {m}"

    if not any_active:
        msg += "\n\n<i>No strong narrative momentum right now.</i>"

    send(msg.strip())


# ===================== RUN =====================
if __name__ == "__main__":
    market_report()
