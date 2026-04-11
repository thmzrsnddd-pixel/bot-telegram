from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import base64
import time

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"
ADMIN_ID = 8584498503

app = Flask(__name__)

bot_app = ApplicationBuilder().token(TOKEN).build()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(bot_app.initialize())

usuarios_funil = set()

# =============================
# MIDIAS (COLE SUAS 25 AQUI)
# =============================

FOTO_START = "AgACAgEAAyEFAATanvxOAAMfadalWki1wP7-1YvoJzGG9b_SDb4AAiQMaxtbAAG5Rm_IZa1EkJk2AQADAgADeQADOwQ"

FOTOS = [
# 👉 COLE TODAS SUAS 25 AQUI
]

VIDEOS = [
# 👉 TODOS OS VÍDEOS
]

# =============================
# PLANOS
# =============================

PLANOS = {
    "isca": {"preco": 4.50, "nome": "🔥 PROMOÇÃO"},
    "upgrade": {"preco": 3.99, "nome": "🔓 LIBERAR RESTO"},
    "leve": {"preco": 6.99, "nome": "😈 LEVE"},
    "pesado": {"preco": 14.99, "nome": "🔥 PESADO"},
    "pesadissimo": {"preco": 22.99, "nome": "💀 PESADÍSSIMO"},
    "pack": {"preco": 10.99, "nome": "📦 COMPLETO"}
}

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano):
    plano_info = PLANOS[plano]

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
        json={
            "items": [{
                "title": plano_info["nome"],
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": plano_info["preco"]
            }],
            "external_reference": f"{user_id}|{plano}"
        }
    )
    return r.json().get("init_point")

def criar_pix(user_id, plano):
    plano_info = PLANOS[plano]

    return requests.post(
        "https://api.mercadopago.com/v1/payments",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "transaction_amount": plano_info["preco"],
            "payment_method_id": "pix",
            "description": plano_info["nome"],
            "payer": {"email": f"user{user_id}@teste.com"},
            "external_reference": f"{user_id}|{plano}"
        }
    ).json()

# =============================
# ENVIO SEGURO DE MIDIAS
# =============================

def enviar_fotos(chat_id):
    for foto in FOTOS:
        for tentativa in range(3):
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                    json={"chat_id": chat_id, "photo": foto},
                    timeout=10
                )
                break
            except:
                time.sleep(1)
        time.sleep(0.8)

def enviar_videos(chat_id):
    for video in VIDEOS:
        for tentativa in range(3):
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                    json={"chat_id": chat_id, "video": video},
                    timeout=10
                )
                break
            except:
                time.sleep(2)
        time.sleep(1.2)

# =============================
# FUNIL (ISCA)
# =============================

async def funil(user_id):
    await asyncio.sleep(120)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "ei... saiu assim? 😏"})

    await asyncio.sleep(480)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "tem coisa ali que eu não mostro sempre 👀"})

    await asyncio.sleep(1200)

    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": "última chance 😈\n\nte libero por R$4,50 👇",
            "reply_markup": {"inline_keyboard": [[{"text": "🔥 ENTRAR", "url": link}]]}
        })

# =============================
# REENGAJAMENTO
# =============================

async def reengajar(user_id):
    await asyncio.sleep(300)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "😈 ainda tá pensando?"})

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in usuarios_funil:
        usuarios_funil.add(user_id)
        loop.create_task(funil(user_id))

    keyboard = [[InlineKeyboardButton("😈 entrar", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption="oii... entra 😈",
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
            [InlineKeyboardButton("😈 LEVE", callback_data="leve")],
            [InlineKeyboardButton("🔥 PESADO", callback_data="pesado")],
            [InlineKeyboardButton("💀 PESADÍSSIMO", callback_data="pesadissimo")],
            [InlineKeyboardButton("📦 COMPLETO", callback_data="pack")]
        ]

        await query.message.reply_text("escolhe 😈", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in PLANOS:
        loop.create_task(reengajar(user_id))

        pix = criar_pix(user_id, query.data)
        link = criar_pagamento(user_id, query.data)

        pix_data = pix.get("point_of_interaction", {}).get("transaction_data", {})
        pix_code = pix_data.get("qr_code")
        pix_qr = pix_data.get("qr_code_base64")

        if pix_qr:
            qr_bytes = base64.b64decode(pix_qr)
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                files={"photo": ("pix.png", qr_bytes)},
                data={"chat_id": user_id}
            )

        texto = "💎 ACESSO IMEDIATO\n\n⏳ conteúdo limitado\n\n"

        if pix_code:
            texto += f"💳 PIX:\n{pix_code}\n\n"

        texto += f"👇 pagar agora\n{link}"

        await query.message.reply_text(texto)

# =============================
# LIBERAR
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    enviar_fotos(ADMIN_ID)
    enviar_videos(ADMIN_ID)

    await update.message.reply_text("✅ enviado")

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    loop.run_until_complete(bot_app.process_update(update))
    return "ok"

# =============================
# WEBHOOK MP
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        pagamento = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        ).json()

        if pagamento["status"] == "approved":
            user_id, plano = pagamento["external_reference"].split("|")
            user_id = int(user_id)

            if plano == "leve":
                enviar_fotos(user_id)
            elif plano == "pesado":
                enviar_videos(user_id)
            else:
                enviar_fotos(user_id)
                enviar_videos(user_id)

    return "ok", 200

# =============================
# ROOT
# =============================

@app.route("/")
def home():
    return "online"

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("liberar", liberar))
bot_app.add_handler(CallbackQueryHandler(botoes))

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
