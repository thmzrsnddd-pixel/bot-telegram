from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import json
import time
import threading

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIP_FILE = os.path.join(BASE_DIR, "vip.json")

# =============================
# TEXTOS (PERSONAGEM TIMIDA)
# =============================

TEXTOS = {
    "start": "🔞😈 Oii... tava te esperando 👀🔥\n\n"
             "🙈 não era pra você ter chegado aqui...\n\n"
             "💋 mas já que chegou...\n"
             "tem coisas minhas que eu nunca postei em lugar nenhum...\n\n"
             "👇 escolhe aí...",

    "vip": "🙈 você chegou perto...\n\n"
           "💋 lá dentro tem coisas que eu fico até com vergonha...\n\n"
           "👇 escolhe um plano...",

    "pagamento": "💰💋 só falta isso...\n\n"
                 "🙈 depois eu te mostro tudo...\n\n"
                 "👇 paga aqui:"
}

# =============================
# PLANOS
# =============================

PLANOS = {
    "1d": {"dias": 1, "preco": 8.99},
    "7d": {"dias": 7, "preco": 14.99},
    "15d": {"dias": 15, "preco": 22.99},
    "promo": {"dias": 1, "preco": 5.00}
}

# =============================
# VIP
# =============================

def carregar_vip():
    if not os.path.exists(VIP_FILE):
        return {}
    with open(VIP_FILE, "r") as f:
        return json.load(f)

def salvar_vip(vips):
    with open(VIP_FILE, "w") as f:
        json.dump(vips, f)

usuarios_vip = carregar_vip()

def is_vip(user_id):
    return str(user_id) in usuarios_vip and time.time() < usuarios_vip[str(user_id)]

def liberar_vip(user_id, dias):
    usuarios_vip[str(user_id)] = time.time() + dias * 86400
    salvar_vip(usuarios_vip)

# =============================
# PAGAMENTO
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
    return data.get("point_of_interaction", {}).get("transaction_data", {}).get("ticket_url")

# =============================
# MIDIAS (DEIXA VAZIO POR ENQUANTO)
# =============================

MIDIAS = [
    # EXEMPLO FUTURO:
    # {"tipo": "foto", "url": "LINK", "texto": "🙈 olha isso..."}
]

def enviar_midias(user_id):
    for m in MIDIAS:
        try:
            if m["tipo"] == "foto":
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={
                    "chat_id": user_id,
                    "photo": m["url"],
                    "caption": m["texto"]
                })
            elif m["tipo"] == "video":
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={
                    "chat_id": user_id,
                    "video": m["url"],
                    "caption": m["texto"]
                })
            time.sleep(2)
        except:
            pass

# =============================
# REENGAJAMENTO
# =============================

def reengajar(user_id):

    def fluxo():
        time.sleep(600)

        if not is_vip(user_id):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": user_id,
                "text": "👀 você ainda tá aí...?\n\n🙈 fiquei meio sem graça...\n\n💋 posso te mostrar mais..."
            })

        time.sleep(3000)

        if not is_vip(user_id):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": user_id,
                "text": "😳 achei que você tinha ido embora...\n\n💭 fiquei pensando em você..."
            })

        time.sleep(18000)

        if not is_vip(user_id):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": user_id,
                "text": "💔 achei que você esqueceu de mim...\n\n🙈 eu tinha separado umas coisas..."
            })

        # OFERTA R$5
        if not is_vip(user_id):
            link = criar_pagamento(user_id, "promo")

            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": user_id,
                "text": f"🤫 só pra você...\n\n💋 consigo liberar por R$5 agora...\n\n👇 {link}"
            })

    threading.Thread(target=fluxo).start()

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔒 VIP", callback_data="vip")]
    ]

    await update.message.reply_text(TEXTOS["start"], reply_markup=InlineKeyboardMarkup(keyboard))

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "vip":
        if not is_vip(user_id):

            keyboard = [
                [InlineKeyboardButton("🚀 ACESSO IMEDIATO", callback_data="7d")],
                [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
                [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")],
                [InlineKeyboardButton("💰 1 DIA", callback_data="1d")]
            ]

            await query.message.reply_text(TEXTOS["vip"], reply_markup=InlineKeyboardMarkup(keyboard))

            reengajar(user_id)

    elif query.data in PLANOS:
        link = criar_pagamento(user_id, query.data)
        await query.message.reply_text(f"{TEXTOS['pagamento']}\n{link}")

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return "ok"

# =============================
# WEBHOOK MP
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        r = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        )

        pagamento = r.json()

        if pagamento["status"] == "approved":
            user_id, plano = pagamento["external_reference"].split("|")
            dias = PLANOS[plano]["dias"]

            liberar_vip(user_id, dias)

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": user_id, "text": f"💋 pronto...\n\n🙈 agora você tá dentro..."}
            )

            enviar_midias(user_id)

    return "ok"

# =============================
# INIT
# =============================

asyncio.run(bot_app.initialize())
requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={PUBLIC_URL}/webhook/{TOKEN}")
