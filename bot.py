from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import sqlite3

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"

MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================
# BANCO DE DADOS
# =============================

conn = sqlite3.connect("vip.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vip_users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def is_vip(user_id):
    cursor.execute("SELECT * FROM vip_users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def add_vip(user_id):
    cursor.execute("INSERT OR IGNORE INTO vip_users (user_id) VALUES (?)", (user_id,))
    conn.commit()

# =============================
# GERAR PAGAMENTO
# =============================

def criar_pagamento(user_id):
    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "transaction_amount": 10,
        "description": "Acesso VIP",
        "payment_method_id": "pix",
        "payer": {
            "email": f"user{user_id}@teste.com"
        },
        "external_reference": str(user_id)
    }

    r = requests.post(url, json=data, headers=headers)
    resposta = r.json()

    return resposta.get("point_of_interaction", {}).get("transaction_data", {}).get("ticket_url")

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    link_pagamento = criar_pagamento(user_id)

    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia", callback_data="previa")],
        [InlineKeyboardButton("🔒 Conteúdo VIP", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar acesso", url=link_pagamento)]
    ]

    with open(os.path.join(BASE_DIR, "foto1.jpg"), "rb") as foto:
        await update.message.reply_photo(
            photo=foto,
            caption="😈 Quer ver tudo? 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "previa":
        with open(os.path.join(BASE_DIR, "foto2.jpg"), "rb") as foto:
            await query.message.reply_photo(
                photo=foto,
                caption="👀 Só uma prévia..."
            )

    elif query.data == "vip":
        if is_vip(user_id):
            with open(os.path.join(BASE_DIR, "video1.mp4"), "rb") as video:
                await query.message.reply_video(
                    video=video,
                    caption="🔥 VIP liberado 😈"
                )
        else:
            await query.message.reply_text("🔒 Libere o VIP para acessar 😈")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)

    async def run():
        await bot_app.initialize()
        await bot_app.process_update(update)

    asyncio.run(run())

    return "ok", 200

# =============================
# WEBHOOK MERCADO PAGO
# =============================

@app.route("/mp", methods=["POST"])
def mp_webhook():
    data = request.json

    try:
        payment_id = data["data"]["id"]

        url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
        headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

        r = requests.get(url, headers=headers)
        pagamento = r.json()

        if pagamento["status"] == "approved":
            user_id = int(pagamento["external_reference"])

            add_vip(user_id)

            # envia mensagem automática
            asyncio.run(bot_app.bot.send_message(
                chat_id=user_id,
                text="🔥 Pagamento aprovado! VIP liberado 😈"
            ))

    except Exception as e:
        print("ERRO MP:", e)

    return "ok", 200

# =============================
# SET WEBHOOKS
# =============================

def set_webhooks():
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook",
                 params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"})

    print("Telegram OK")

set_webhooks()
