from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import asyncio
import requests

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# COMANDO
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 /start recebido")
    await update.message.reply_text("🔥 Bot funcionando!")

bot_app.add_handler(CommandHandler("start", start))

# =============================
# ROTAS
# =============================

@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, bot_app.bot)

    # executa async dentro do Flask corretamente
    asyncio.run(bot_app.process_update(update))

    return "ok", 200

# =============================
# INICIAR BOT
# =============================

async def iniciar_bot():
    print("🚀 Iniciando bot...")

    await bot_app.initialize()
    await bot_app.start()

    # configurar webhook
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    r = requests.get(url, params={"url": webhook_url})
    print("Webhook:", r.text)


# =============================
# START APP
# =============================

if __name__ == "__main__":
    import threading

    # inicia o bot em paralelo
    threading.Thread(target=lambda: asyncio.run(iniciar_bot())).start()

    # inicia servidor web (Render usa porta 10000)
    app.run(host="0.0.0.0", port=10000)
