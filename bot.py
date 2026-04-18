from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import requests
import os
import time
import random

# =============================
# CONFIG
# =============================

TOKEN = 
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"
ADMIN_ID = 8584498503

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# BANCO
# =============================

usuarios = {}

def registrar(user_id):
    if user_id not in usuarios:
        usuarios[user_id] = {
            "clicou": None,
            "comprou": False,
            "tentativas": 0
        }

# =============================
# MIDIAS (MANTIDAS)
# =============================

FOTOS_LEVE = [
"AgACAgEAAyEFAATanvxOAAMfadalWki1wP7-1YvoJzGG9b_SDb4AAiQMaxtbAAG5Rm_IZa1EkJk2AQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMgadalWpQu9iHfYUWKgZ7DtzZRqI8AAicMaxtbAAG5RiyZJaeK4ptQAQADAgADeQADOwQ"
]

VIDEOS_PESADO = [
"BAACAgEAAxkBAAIDOWnWqNs-1FpAl43ilynlUwZ0g6g8AAJICAAC9KC4Rh5FmcPCMztcOwQ",
"BAACAgEAAxkBAAIDOmnWqNv51sHmOSI4skR7Leg_niGDAAJACAAC9KC4RoWPxz3SVNSNOwQ"
]

VIDEOS_PESADISSIMO = [
"BAACAgEAAxkBAAIDPWnWqNtgenHSZrHn6qLFSdzOW-tNAAJKCAAC9KC4RrM2wJoZDWpWOwQ"
]

VIDEOS_COMPLETO = [
"BAACAgEAAxkBAAIDQ2nWqNuh23ry1SLL0DzdlLnKN9QrAAJFCAAC9KC4RtQY7wGiIsYFOwQ"
]

PLANOS = {
    "leve": 5.00,
    "pesado": 8.99,
    "pesadissimo": 12.99,
    "completo": 15.99
}

# =============================
# PREÇO DINÂMICO
# =============================

def preco_dinamico(user_id, plano):
    base = PLANOS[plano]
    tentativas = usuarios[user_id]["tentativas"]

    if tentativas >= 3:
        return base - 1.00
    if tentativas == 0:
        return base + 1.00

    return base

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano, extra=0):
    preco = preco_dinamico(user_id, plano) + extra

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
        json={
            "items": [{
                "title": plano,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco
            }],
            "external_reference": f"{user_id}|{plano}"
        }
    )
    return r.json().get("init_point")

# =============================
# REMARKETING
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    if usuarios[user_id]["comprou"]:
        return

    plano = usuarios[user_id]["clicou"]
    link = criar_pagamento(user_id, plano)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id,
              "text": "👀 você sumiu..."})

    await asyncio.sleep(5)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id,
              "text": f"😈 não vai entrar?\n👉 {link}"})

# =============================
# START (🔥 NOVA ABERTURA)
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    registrar(user_id)

    # simula humano
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendChatAction",
                  json={"chat_id": user_id, "action": "typing"})
    time.sleep(2)

    await update.message.reply_text(
        "👀 ei...\n\nnão sei se devia te responder aqui..."
    )

    time.sleep(2)

    await update.message.reply_text(
        "😳 você chegou meio rápido...\n\nnormalmente não mostro isso assim"
    )

    time.sleep(2)

    # envia 1 mídia (isca)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                  json={"chat_id": user_id, "photo": FOTOS_LEVE[0]})

    time.sleep(2)

    keyboard = [[InlineKeyboardButton("😈 quero ver mais", callback_data="vip")]]

    await update.message.reply_text(
        "😏 isso foi só um pedacinho...\n\nmas cuidado com o que você clica agora...",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    registrar(user_id)

    if query.data == "vip":

        keyboard = [
            [InlineKeyboardButton("😈 leve", callback_data="leve")],
            [InlineKeyboardButton("🔥 pesado", callback_data="pesado")],
            [InlineKeyboardButton("👑 pesadíssimo", callback_data="pesadissimo")],
            [InlineKeyboardButton("💎 completo", callback_data="completo")]
        ]

        await query.message.reply_text(
            "😈 escolhe seu nível...",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        usuarios[user_id]["clicou"] = query.data
        usuarios[user_id]["tentativas"] += 1

        asyncio.create_task(remarketing(user_id))

        link = criar_pagamento(user_id, query.data)

        keyboard = [[InlineKeyboardButton("🔥 desbloquear agora", url=link)]]

        await query.message.reply_text(
            "⏳ acesso limitado...\n🔥 muita gente entrou hoje",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# ENTREGA
# =============================

def enviar_leve(chat_id):
    for f in FOTOS_LEVE:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": f})

def enviar_pesado(chat_id):
    for v in VIDEOS_PESADO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": v})

def enviar_pesadissimo(chat_id):
    for v in VIDEOS_PESADISSIMO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": v})

def enviar_completo(chat_id):
    for f in FOTOS_LEVE:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": f})

    for v in VIDEOS_PESADO + VIDEOS_PESADISSIMO + VIDEOS_COMPLETO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": v})

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

            usuarios[user_id]["comprou"] = True

            if plano == "leve":
                enviar_leve(user_id)
            elif plano == "pesado":
                enviar_pesado(user_id)
            elif plano == "pesadissimo":
                enviar_pesadissimo(user_id)
            elif plano == "completo":
                enviar_completo(user_id)

    return "ok", 200

# =============================
# TELEGRAM WEBHOOK
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)

    async def process():
        await bot_app.initialize()
        await bot_app.process_update(update)

    asyncio.run(process())
    return "ok"

@app.route("/")
def home():
    return "online"

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# RUN
# =============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
