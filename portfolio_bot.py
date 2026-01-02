import os
import json
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("PORTFOLIO_CHAT_ID")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON")

bot = Bot(token=BOT_TOKEN)

# -------------------------
# DATA SOURCES
# -------------------------

def fetch_coingecko(coin_ids):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),
        "price_change_percentage": "24h,7d"
    }
    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data:
        return None
    return {c["id"]: c for c in data}


def fetch_cryptocompare(symbols):
    url = "https://min-api.cryptocompare.com/data/pricemultifull"
    params = {
        "fsyms": ",".join(symbols),
        "tsyms": "USD"
    }
    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json().get("RAW", {})
    if not data:
        return None
    return data


# -------------------------
# MAIN LOGIC
# -------------------------

def run_portfolio_bot():
    now = datetime.utcnow().strftime("%d %b %Y | %H:%M UTC")

    try:
        portfolio = json.loads(PORTFOLIO_JSON)
    except Exception:
        bot.send_message(chat_id=CHAT_ID, text="⚠️ Invalid portfolio JSON.")
        return

    coin_ids = list(portfolio.keys())

    # ---- Try CoinGecko first
    cg_data = fetch_coingecko(coin_ids)

    use_fallback = False
    if not cg_data:
        use_fallback = True

    # ---- Fallback to CryptoCompare
    cc_data = None
    if use_fallback:
        symbol_map = {
            "vechain": "VET",
            "optimism": "OP",
            "avalanche-2": "AVAX",
            "near": "NEAR",
            "arweave": "AR"
        }
        symbols = [symbol_map[c] for c in coin_ids if c in symbol_map]
        cc_data = fetch_cryptocompare(symbols)

        if not cc_data:
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"📊 PORTFOLIO INTELLIGENCE\n🕒 {now}\n\n⚠️ All market data sources unavailable."
            )
            return

    # -------------------------
    # BUILD REPORT
    # -------------------------

    lines = [
        "📊 PORTFOLIO INTELLIGENCE",
        f"🕒 {now}",
        "",
        "📦 Allocation Overview"
    ]

    for coin, weight in portfolio.items():
        if not use_fallback:
            price = cg_data[coin]["current_price"]
            chg = cg_data[coin].get("price_change_percentage_24h", 0)
        else:
            sym = symbol_map[coin]
            raw = cc_data[sym]["USD"]
            price = raw["PRICE"]
            chg = raw["CHANGEPCT24HOUR"]

        lines.append(
            f"• {coin.upper():<10} {weight:.1f}% | ${price:.2f} | {chg:+.2f}% (24h)"
        )

    # -------------------------
    # STRATEGIC INSIGHT
    # -------------------------

    lines += [
        "",
        "🧠 STRATEGY VIEW",
        "• Short-term: Volatility-driven, watch BTC correlation",
        "• Mid-term: Infra + L1 heavy — rotation dependent",
        "• Long-term: Strong fundamental exposure, but concentration risk on VET"
    ]

    bot.send_message(chat_id=CHAT_ID, text="\n".join(lines))


if __name__ == "__main__":
    run_portfolio_bot()
