import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Import your bots
import market_bot
import action_bot
import portfolio_bot

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------------- COMMAND HANDLERS ----------------

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Running Market Bot...")
    market_bot.run()

async def action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Running Action Bot...")
    action_bot.run()

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Running Portfolio Bot...")
    portfolio_bot.run()

async def runall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Running ALL bots...")
    market_bot.run()
    action_bot.run()
    portfolio_bot.run()

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/market – Run market scan\n"
        "/action – Run action scan\n"
        "/portfolio – Run portfolio analysis\n"
        "/runall – Run everything\n"
        "/status – Bot status"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Beast Bot online & listening")

# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("action", action))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("runall", runall))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))

    print("🤖 Beast Bot listening on Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
