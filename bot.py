import threading
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"

app = Flask(__name__)
bot_app = None

# =============================
# TELEGRAM BOT
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 /start recebido")
    await update.message.reply_text("🔥 Bot funcionando!")

async def iniciar_bot():
    global bot_app

    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))

    await bot_app.initialize()
    await bot_app.start()

    print("🤖 Bot iniciado!")

# =============================
# WEBHOOK
# =============================

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    global bot_app

    if bot_app is None:
        return "ok", 200

    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)

    bot_app.update_queue.put_nowait(update)

    return "ok", 200

# =============================
# INICIAR TUDO
# =============================

def run_async():
    asyncio.run(iniciar_bot())

def iniciar_webhook():
    import requests

    print("🌐 Configurando webhook...")

    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    r = requests.get(url, params={"url": webhook_url})
    print("Webhook:", r.text)

    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    print("🚀 Iniciando aplicação...")

    threading.Thread(target=run_async).start()
    threading.Thread(target=iniciar_webhook).start()
