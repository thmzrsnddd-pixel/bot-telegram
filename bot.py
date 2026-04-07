from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import asyncio
import requests
import os
import json
import time

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔒 VIP", callback_data="vip")]
    ]

    await update.message.reply_text(
        "🔞😈 Oii... tava te esperando 👀🔥\n\n"
        "🙈 não era pra você ter chegado aqui...\n\n"
        "💋 mas já que chegou...\n"
        "tem coisas minhas que eu nunca postei...\n\n"
        "👇 clica abaixo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "vip":
        keyboard = [
            [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
            [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")],
            [InlineKeyboardButton("💰 1 DIA", callback_data="1d")]
        ]

        await query.message.reply_text(
            "🙈 você chegou perto...\n\n"
            "💋 escolhe um plano...",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# PEGAR FILE_ID (IMPORTANTE)
# =============================

async def pegar_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"📸 FOTO ID:\n{file_id}")

    elif update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 VIDEO ID:\n{file_id}")

    elif update.message.document:
        file_id = update.message.document.file_id
        await update.message.reply_text(f"📁 ARQUIVO ID:\n{file_id}")

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))
bot_app.add_handler(MessageHandler(filters.ALL, pegar_id))

# =============================
# WEBHOOK TELEGRAM (CORRIGIDO)
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)

    async def process():
        await bot_app.initialize()
        await bot_app.process_update(update)

    asyncio.run(process())

    return "ok", 200

# =============================
# ROOT (IMPORTANTE PRO RENDER)
# =============================

@app.route("/")
def home():
    return "BOT ONLINE", 200

# =============================
# SET WEBHOOK
# =============================

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    requests.get(url, params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"})

set_webhook()

# =============================
# START FLASK (IMPORTANTE)
# =============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
