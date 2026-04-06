import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"

app = Flask(__name__)

# ================= BOT =================

bot_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot funcionando!")

bot_app.add_handler(CommandHandler("start", start))

# ================= WEBHOOK =================

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, bot_app.bot)
    await bot_app.initialize()
    await bot_app.process_update(update)

    return "ok", 200

# ================= START =================

if __name__ == "__main__":
    import requests

    print("🚀 Iniciando...")

    # seta webhook
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
