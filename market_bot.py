import os
import requests
from datetime import datetime

# ===== ENV =====
BOT_TOKEN = os.environ["BOT_TOKEN"]
MARKET_CHAT_ID = os.environ["MARKET_CHAT_ID"]

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

CG_GLOBAL = "https://api.coingecko.com/api/v3/global"
CG_MARKETS = "https://api.coingecko.com/api/v3/coins/markets"

HEADERS = {"accept": "application/json"}

# ===== HELPERS =====
def send(msg):
    try:
        requests.post(
            TG_URL,
            data={
                "chat_id": MARKET_CHAT_ID,
                "text": msg,
                "parse_mode": "HTML"
            },
            timeout=20
        )
    except Exception as e:
        print("Telegram error:", e)


def get_global():
    r = requests.get(CG_GLOBAL, timeout=20)
    return r.json()["data"]


def get_coins(category):
    params = {
        "vs_currency": "usd",
        "category": category,
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "price_change_percentage": "7d"
    }
    r = requests.get(CG_MARKETS, params=params, timeout=20)
    return r.json()


# ===== LOGIC =====
def analyze_narrative(name, category):
    try:
        coins = get_coins(category)
    except:
        return f"🔴 {name}: Data error"

    movers = []
    for c in coins:
        pct = c.get("price_change_percentage_7d")
        if pct and pct > 15:
            movers.append(f"{c['symbol'].upper()} +{pct:.1f}%")

    if not movers:
        return f"🟡 {name}: Quiet / no momentum"

    return f"🟢 {name}: " + ", ".join(movers[:4])


def market_report():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    global_data = get_global()

    btc_d = global_data["market_cap_percentage"]["btc"]
    eth_d = global_data["market_cap_percentage"]["eth"]

    if btc_d > 52:
        risk = "Risk-Off"
    elif btc_d < 48:
        risk = "Risk-On"
    else:
        risk = "Neutral"

    msg = f"""
🧠 <b>MARKET SNAPSHOT</b>
🕒 {now}

<b>Risk Regime:</b> {risk}

<b>Dominance</b>
• BTC: {btc_d:.2f}%
• ETH: {eth_d:.2f}%

<b>Narrative Movers</b>
"""

    msg += "\n" + analyze_narrative("AI / Compute", "artificial-intelligence")
    msg += "\n" + analyze_narrative("RWA / Tokenization", "real-world-assets")
    msg += "\n" + analyze_narrative("Layer 2s", "layer-2")
    msg += "\n" + analyze_narrative("DePIN / Infra", "depin")
    msg += "\n" + analyze_narrative("Gaming", "gaming")
    msg += "\n" + analyze_narrative("Privacy", "privacy-coins")

    send(msg.strip())


# ===== RUN =====
if __name__ == "__main__":
    market_report()        "price_change_percentage": "24h,7d"
    }
    r = requests.get(url, params=params, timeout=20)
    return r.json()

def get_btc_dominance():
    r = requests.get(f"{COINGECKO}/global", timeout=20).json()
    return round(r["data"]["market_cap_percentage"]["btc"], 2)

# ================== NARRATIVES ==================
NARRATIVES = {
    "AI / Compute": ["render-token", "fetch-ai", "akash-network"],
    "Privacy Coins": ["zcash", "monero"],
    "Layer 2s": ["arbitrum", "optimism", "polygon"],
    "Gaming": ["immutable-x", "gala", "beam"],
    "DePIN / Infra": ["helium", "filecoin"]
}

def analyze_narratives(coins):
    results = {}

    for name, ids in NARRATIVES.items():
        movers = []
        for c in coins:
            if c["id"] in ids:
                if c.get("price_change_percentage_7d_in_currency", 0) > 15:
                    movers.append(
                        f"{c['symbol'].upper()} +{round(c['price_change_percentage_7d_in_currency'],1)}%"
                    )

        if movers:
            results[name] = ("Strong", movers)
        else:
            results[name] = ("Weak", [])

    return results

# ================== MACRO ==================
def macro_score(btc_d):
    if btc_d > 55:
        return 35, "Risk-Off"
    elif btc_d > 48:
        return 50, "Neutral"
    else:
        return 70, "Risk-On"

# ================== REPORT ==================
def market_report():
    coins = get_top_coins()
    btc_d = get_btc_dominance()

    score, regime = macro_score(btc_d)
    narratives = analyze_narratives(coins)

    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    msg = f"""🧠 <b>MARKET SNAPSHOT</b>
⏰ {now}

<b>Macro</b>
• BTC Dominance: {btc_d}%
• Regime: {regime}
• Macro Score: {score}/100

<b>Narratives</b>
"""

    for n, data in narratives.items():
        strength, movers = data

        if strength == "Strong":
            emoji = "🟢"
        else:
            emoji = "🔴"

        msg += f"\n{emoji} <b>{n}</b>: {strength}"
        if movers:
            msg += "\n   " + ", ".join(movers)

    # BTC dominance conflict warning
    if btc_d > 55:
        msg += "\n\n⚠️ <b>BTC dominance high → alts suppressed</b>"

    send(msg)

# ================== RUN ==================
if __name__ == "__main__":
    market_report()        data={
            "chat_id": MARKET_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        },
        timeout=20
    )

# =========================
# DATA
# =========================
def get_market():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS,
        "order": "market_cap_desc",
        "per_page": TOP_N,
        "page": 1,
        "price_change_percentage": "24h,7d"
    }
    return requests.get(url, params=params, timeout=30).json()

# =========================
# MACRO
# =========================
def btc_metrics(market):
    total_mc = 0
    btc_mc = 0
    btc_24h = 0

    for c in market:
        mc = c.get("market_cap") or 0
        total_mc += mc

        if c.get("id") == "bitcoin":
            btc_mc = mc
            btc_24h = c.get("price_change_percentage_24h") or 0

    if total_mc == 0:
        return None, None

    dominance = round((btc_mc / total_mc) * 100, 2)
    return dominance, btc_24h

def macro_score(btc_dom, btc_24h):
    score = 50

    if btc_24h < -2:
        score += 10
    if btc_24h > 3:
        score -= 5
    if btc_dom is not None and btc_dom > 52:
        score -= 10
    if btc_dom is not None and btc_dom < 48:
        score += 5

    return max(0, min(100, score))

# =========================
# NARRATIVES
# =========================
def narrative_check(market, ids):
    changes = []

    for c in market:
        if c.get("id") in ids:
            v = c.get("price_change_percentage_7d_in_currency")
            if v is not None:
                changes.append(v)

    if not changes:
        return "Data error", 0

    avg = sum(changes) / len(changes)

    if avg >= STRONG_MOVE:
        strength = "Strong"
    elif avg >= MODERATE_MOVE:
        strength = "Moderate"
    else:
        strength = "Weak"

    return strength, avg

def velocity_label(v):
    if v >= 20:
        return "🔥 Accelerating"
    if v >= 10:
        return "⬆ Rising"
    if v >= 0:
        return "➖ Flat"
    return "⬇ Cooling"

# =========================
# REPORT
# =========================
def market_report():
    market = get_market()

    now = datetime.now(timezone.utc).strftime("%d %b %Y | %H:%M UTC")

    btc_dom, btc_24h = btc_metrics(market)
    score = macro_score(btc_dom, btc_24h)

    if score >= 65:
        regime = "Risk-On"
    elif score <= 35:
        regime = "Risk-Off"
    else:
        regime = "Neutral"

    msg = (
        f"<b>🧠 MARKET SNAPSHOT</b>\n"
        f"🕒 {now}\n\n"
        f"<b>Risk Regime:</b> {regime}\n"
        f"<b>Macro Score:</b> {score}/100\n\n"
        f"<b>BTC 24h:</b> {btc_24h:.2f}%\n"
        f"<b>BTC Dominance:</b> {btc_dom}%\n\n"
        f"<b>Narratives</b>\n"
    )

    strengths = {}

    for name, ids in NARRATIVES.items():
        strength, avg = narrative_check(market, ids)
        strengths[name] = avg

        if strength == "Strong":
            emoji = "🟢"
        elif strength == "Moderate":
            emoji = "🟡"
        else:
            emoji = "🔴"

        vel = velocity_label(avg)

        msg += f"{emoji} <b>{name}</b>: {strength} ({vel})\n"

    # =========================
    # ROTATION
    # =========================
    strongest = max(strengths, key=strengths.get)
    weakest = min(strengths, key=strengths.get)

    if strengths[strongest] - strengths[weakest] >= 15:
        msg += f"\n🔁 <b>Rotation:</b> {weakest} ➜ {strongest}\n"

    # =========================
    # BTC CONFLICT
    # =========================
    if btc_24h > 2 and any(v > 8 for v in strengths.values()):
        msg += "\n⚠️ <b>BTC dominance conflict:</b> Alts running with BTC\n"

    send(msg.strip())

# =========================
# RUN
# =========================
if __name__ == "__main__":
    market_report()            "chat_id": MARKET_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        },
        timeout=20
    )

def get_market():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS,
        "order": "market_cap_desc",
        "per_page": TOP_N,
        "page": 1,
        "price_change_percentage": "24h,7d"
    }
    return requests.get(url, params=params, timeout=30).json()

# =========================
# MACRO
# =========================
def btc_dominance(market):
    btc = None
    total = 0

    for c in market:
        mc = c.get("market_cap") or 0
        total += mc
        if c.get("id") == "bitcoin":
            btc = c

    if not btc or total == 0:
        return None, None

    dom = round((btc["market_cap"] / total) * 100, 2)
    btc_24h = btc.get("price_change_percentage_24h") or 0
    return dom, btc_24h

def macro_score(btc_dom, btc_24h):
    score = 50

    if btc_24h < -2:
        score += 10
    if btc_24h > 3:
        score -= 5
    if btc_dom and btc_dom > 52:
        score -= 10
    if btc_dom and btc_dom < 48:
        score += 5

    return max(0, min(100, score))

# =========================
# NARRATIVES
# =========================
def narrative_check(market, ids):
    coins = [c for c in market if c.get("id") in ids]

    if not coins:
        return "Data error", 0

    avg_7d = 0
    count = 0

    for c in coins:
        v = c.get("price_change_percentage_7d_in_currency")
        if v is not None:
            avg_7d += v
            count += 1

    if count == 0:
        return "Data error", 0

    avg_7d = avg_7d / count

    if avg_7d >= STRONG_MOVE:
        strength = "Strong"
    elif avg_7d >= MODERATE_MOVE:
        strength = "Moderate"
    else:
        strength = "Weak"

    return strength, avg_7d

def velocity_label(v):
    if v >= 20:
        return "🔥 Accelerating"
    elif v >= 10:
        return "⬆ Rising"
    elif v >= 0:
        return "➖ Flat"
    else:
        return "⬇ Cooling"

# =========================
# REPORT
# =========================
def market_report():
    market = get_market()

    now = datetime.now(timezone.utc).strftime("%d %b %Y | %H:%M UTC")

    btc_dom, btc_24h = btc_dominance(market)
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
        v, avg = narrative_check(market, ids)
        strengths[name] = avg

        if v == "Strong":
            emoji = "🟢"
        elif v == "Moderate":
            emoji = "🟡"
        else:
            emoji = "🔴"

        vel = velocity_label(avg)

        msg += f"{emoji} <b>{name}</b>: {v} ({vel})\n"

    # =========================
    # ROTATION
    # =========================
    top = max(strengths, key=strengths.get)
    bottom = min(strengths, key=strengths.get)

    if strengths[top] - strengths[bottom] >= 15:
        msg += f"\n🔁 <b>Rotation:</b> {bottom} ➜ {top}\n"

    # =========================
    # BTC CONFLICT
    # =========================
    if btc_24h > 2 and any(v > 8 for v in strengths.values()):
        msg += "\n⚠️ <b>BTC dominance conflict:</b> Alts running with BTC\n"

    send(msg.strip())

# =========================
# RUN
# =========================
if __name__ == "__main__":
    market_report()        strength = "Weak"

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
  if v == "Strong":
    emoji = "🟢"
elif v == "Moderate":
    emoji = "🟡"
else:
    emoji = "🔴"  market_report()        emoji = "🟢" if v == "Strong" else "🟡" if v == "Moderate" else "🔴"
        msg += f"\n{emoji} {k}: {v}"

    send(msg)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    market_report()
