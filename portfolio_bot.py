import os
import json
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send(msg):
    requests.post(
        TG_URL,
        json={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True},
        timeout=15
    )

# ---------- DATA SOURCES ----------

def fetch_coingecko(ids):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(ids),
                "price_change_percentage": "24h,7d"
            },
            timeout=15
        )
        if r.status_code != 200:
            return None
        data = r.json()
        return data if isinstance(data, list) and data else None
    except Exception:
        return None

def fetch_cryptocompare(symbols):
    try:
        r = requests.get(
            "https://min-api.cryptocompare.com/data/pricemultifull",
            params={"fsyms": ",".join(symbols), "tsyms": "USD"},
            timeout=15
        )
        raw = r.json().get("RAW", {})
        return raw if raw else None
    except Exception:
        return None

# ---------- MAIN ----------

def run():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    portfolio = json.loads(PORTFOLIO_JSON)

    id_to_symbol = {
        "vechain": "VET",
        "optimism": "OP",
        "avalanche-2": "AVAX",
        "near": "NEAR",
        "arweave": "AR"
    }

    ids = list(portfolio.keys())
    symbols = [id_to_symbol[i] for i in ids if i in id_to_symbol]

    data = fetch_coingecko(ids)
    source = "CoinGecko"

    if not data:
        cc = fetch_cryptocompare(symbols)
        source = "CryptoCompare"
        data = []

        if cc:
            for cid, sym in id_to_symbol.items():
                if sym in cc:
                    usd = cc[sym]["USD"]
                    data.append({
                        "id": cid,
                        "symbol": sym.lower(),
                        "current_price": usd["PRICE"],
                        "price_change_percentage_24h": usd["CHANGEPCT24HOUR"],
                        "price_change_percentage_7d_in_currency": None
                    })

    # ---------- BUILD MESSAGE ----------

    lines = [
        "📊 PORTFOLIO INTELLIGENCE",
        f"🕒 {now}",
        f"📡 Data source: {source}",
        ""
    ]

    if not data:
        lines += [
            "⚠️ Live price data unavailable.",
            "",
            "🧠 STRATEGIC VIEW (Data-independent)",
            "• Portfolio is infra + L1 heavy",
            "• High single-asset exposure (VET ~29%)",
            "• Low hedge / BTC-beta exposure",
            "• Works best in risk-on environments"
        ]
        send("\n".join(lines))
        return

    total_infra = 0
    for c in data:
        w = portfolio.get(c["id"], 0)
        price = c["current_price"]
        p24 = c.get("price_change_percentage_24h", 0)
        p7 = c.get("price_change_percentage_7d_in_currency")

        lines.append(
            f"• {c['symbol'].upper():<5} | {w:.1f}% | ${price:.2f} | "
            f"{p24:+.2f}% (24h)"
        )

        if c["id"] in ["vechain", "optimism", "avalanche-2", "near"]:
            total_infra += w

    # ---------- STRATEGY ----------

    lines += [
        "",
        "🧠 TIME HORIZON ANALYSIS",
        "",
        "⏱ SHORT TERM (days–weeks)",
        "• Sensitive to BTC chop & funding shifts",
        "• Overweight positions amplify volatility",
        "",
        "📆 MID TERM (weeks–months)",
        "• Strong infra correlation → rotation risk",
        "• Needs narrative tailwinds (AI, L2 activity)",
        "",
        "🕰 LONG TERM (cycle)",
        "• Solid fundamental exposure",
        "• Concentration risk if single narrative underperforms",
        "",
        "⚠️ RISK NOTES",
        f"• Infra + L1 exposure ≈ {round(total_infra,1)}%",
        "• Consider diversification for drawdown control"
    ]

    send("\n".join(lines))

if __name__ == "__main__":
    run()
