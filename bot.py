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
import time
import random

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# DIGITANDO
# =============================

def digitando(chat_id, tempo=2):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"}
    )
    time.sleep(tempo)

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
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBYmnVAAHAeHwHLWHdbsLbnNUvLIaoVgAC8QcAAqZgqUbtoS5YWN_WPjsE"},
]

# =============================
# CONTROLE
# =============================

pagamentos_processados = set()

# =============================
# PAGAMENTO (CORRIGIDO)
# =============================

def criar_pagamento(user_id, plano):
    plano_info = PLANOS[plano]

    r = requests.post(
        "https://api.mercadopago.com/v1/payments",
        json={
            "transaction_amount": plano_info["preco"],
            "description": f"Plano {plano}",
            "payment_method_id": "pix",
            "payer": {"email": "teste@test.com"},
            "external_reference": f"{user_id}|{plano}"
        },
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
    )

    data = r.json()

    try:
        qr = data["point_of_interaction"]["transaction_data"]["qr_code"]
        return qr
    except:
        return "Erro ao gerar pagamento, tente novamente."

# =============================
# START (TRÁFEGO)
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.chat_id
    origem = context.args[0] if context.args else "normal"

    if origem == "tiktok":
        texto = "🙈 você veio do tiktok..."
    elif origem == "insta":
        texto = "💋 veio do insta né..."
    elif origem == "promo":
        texto = "🔥 você pegou a promoção..."
    else:
        texto = "oi... 🙈"

    keyboard = [
        [InlineKeyboardButton("🔒 ACESSAR VIP", callback_data="vip")]
    ]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption=texto,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    digitando(user_id, 2)

    await update.message.reply_text(
        "não sei se devia falar com você... 🙈\nmas fiquei curiosa..."
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "vip":

        digitando(user_id, 2)

        await query.message.reply_text(
            "🙈 você veio até aqui...\n💋 fico com vergonha...\nescolhe um plano..."
        )

        keyboard = [
            [InlineKeyboardButton("💰 1 DIA - R$5", callback_data="1d")],
            [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
            [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        digitando(user_id, 2)

        pix = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"💰 último passo...\n\ncopia e cola no seu banco 👇\n\n{pix}"
        )

# =============================
# RESPOSTAS
# =============================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.chat_id
    texto = update.message.text.lower()

    digitando(user_id, random.randint(1,2))

    if "oi" in texto:
        await update.message.reply_text(
            "oi... 🙈\nvocê voltou...\n💋 tava pensando em você..."
        )
    else:
        await update.message.reply_text(
            "🙈 você fala assim...\n💋 fico sem reação..."
        )

# =============================
# ENTREGA
# =============================

def enviar_midias(chat_id):

    digitando(chat_id, 2)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "🙈 tá bom...\nvou te mostrar..."}
    )

    for midia in MIDIAS_VIP:

        digitando(chat_id, 2)

        if midia["tipo"] == "foto":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": midia["id"]}
            )
        else:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                json={"chat_id": chat_id, "video": midia["id"]}
            )

# =============================
# WEBHOOK MP
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    try:
        if data.get("type") == "payment":

            payment_id = data["data"]["id"]

            if payment_id in pagamentos_processados:
                return "ok", 200

            pagamentos_processados.add(payment_id)

            pagamento = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
            ).json()

            if pagamento["status"] == "approved":
                user_id, plano = pagamento["external_reference"].split("|")
                enviar_midias(user_id)

    except Exception as e:
        print("ERRO:", e)

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
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# =============================
# WEBHOOK
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
