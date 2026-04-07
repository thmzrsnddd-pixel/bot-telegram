from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import asyncio
import requests
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
# PLANOS
# =============================

PLANOS = {
    "1d": {"dias": 1, "preco": 5.00},
    "7d": {"dias": 7, "preco": 14.99},
    "15d": {"dias": 15, "preco": 22.99}
}

# =============================
# MIDIAS
# =============================

FOTO_START = "AgACAgEAAxkBAAIBW2nVAAHA4MmTOu-BxgLp5jg8Ki_BSwACGAxrG6ZgqUZa618MB7ra7wEAAwIAA3kAAzsE"
VIDEO_VIP = "BAACAgEAAyEFAATanvxOAAMUadUHHCYG4cpssnNLzoS_9tzrQAgAAvoHAAKmYKlGY1cOvM0Wqzw7BA"

MIDIAS_VIP = [
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXGnVAAHAb5B3BdUxiosov-1dgCmJKwACFwxrG6ZgqUaMyF1kSngZSgEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXWnVAAHAbVGKwRoQSJjZ3BNnHh7NqQACGQxrG6ZgqUbCJc8OBDvJYwEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXmnVAAHAtv9eH4pPF3wWgNnAbEAOHwACGgxrG6ZgqUbO0Js_MMVsjgEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBX2nVAAHAXPd6uwjw7pDhicxr3YTsUwACGwxrG6ZgqUaPWpNpw3MxMAEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBYGnVAAHAbnPgUhD1y1LTKG71eWe53AACHAxrG6ZgqUZMfSFoc5X4AQEAAwIAA3kAAzsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBYmnVAAHAeHwHLWHdbsLbnNUvLIaoVgAC8QcAAqZgqUbtoS5YWN_WPjsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBY2nVAAHAYPdq3KsobU8gX9sl2dp2GwAC7AcAAqZgqUYDC8pyBIDwsDsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBZGnVAAHAO7O3Vtsh6t7BzFAgCgkX7QAC9gcAAqZgqUaNNQWAeadz-DsE"},
]

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano):
    plano_info = PLANOS[plano]

    url = "https://api.mercadopago.com/v1/payments"

    payload = {
        "transaction_amount": plano_info["preco"],
        "description": f"Plano {plano}",
        "payment_method_id": "pix",
        "payer": {"email": "teste@test.com"},
        "external_reference": f"{user_id}|{plano}"
    }

    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    return data.get("point_of_interaction", {}).get("transaction_data", {}).get("ticket_url")

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🔒 ACESSAR VIP", callback_data="vip")]
    ]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption=(
            "🔞😈 Oii... tava te esperando 👀🔥\n\n"
            "🙈 não era pra você ter chegado aqui...\n\n"
            "💋 mas já que chegou...\n"
            "tem coisas minhas que eu nunca mostrei...\n\n"
            "👇 toca aqui..."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "vip":

        keyboard = [
            [InlineKeyboardButton("💰 1 DIA - R$5", callback_data="1d")],
            [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
            [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption=(
                "🙈 você chegou longe...\n\n"
                "💋 isso aqui é só uma parte...\n\n"
                "👇 escolhe um plano..."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"💰 Finaliza aqui:\n{link}"
        )

# =============================
# ENVIAR MIDIAS
# =============================

def enviar_midias(chat_id):
    for midia in MIDIAS_VIP:
        if midia["tipo"] == "foto":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": midia["id"]}
            )
        elif midia["tipo"] == "video":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                json={"chat_id": chat_id, "video": midia["id"]}
            )

# =============================
# WEBHOOK MERCADO PAGO
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    try:
        if data.get("type") == "payment":
            payment_id = data["data"]["id"]

            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

            r = requests.get(url, headers=headers)
            pagamento = r.json()

            if pagamento["status"] == "approved":
                ref = pagamento["external_reference"]
                user_id, plano = ref.split("|")

                enviar_midias(user_id)

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={
                        "chat_id": user_id,
                        "text": "🔓 acesso liberado..."
                    }
                )

    except Exception as e:
        print("ERRO MP:", e)

    return "ok", 200

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)

    async def process():
        await bot_app.initialize()
        await bot_app.process_update(update)

    asyncio.run(process())

    return "ok", 200

@app.route("/")
def home():
    return "online", 200

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# SET WEBHOOK
# =============================

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

set_webhook()

# =============================
# RUN
# =============================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
