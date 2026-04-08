from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import asyncio
import requests
import time
import json
import os
import random

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

DB_FILE = "usuarios.json"
INTERESSE_FILE = "interesse.json"

# =============================
# MIDIA
# =============================

FOTO_START = "AgACAgEAAxkBAAIBW2nVAAHA4MmTOu-BxgLp5jg8Ki_BSwACGAxrG6ZgqUZa618MB7ra7wEAAwIAA3kAAzsE"
VIDEO_VIP = "BAACAgEAAyEFAATanvxOAAMUadUHHCYG4cpssnNLzoS_9tzrQAgAAvoHAAKmYKlGY1cOvM0Wqzw7BA"

# =============================
# BANCO
# =============================

def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def salvar_usuarios(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def liberar_acesso(user_id, dias):
    usuarios = carregar_usuarios()

    if dias == 999:
        usuarios[str(user_id)] = 9999999999
    else:
        expira = int(time.time()) + dias * 86400
        usuarios[str(user_id)] = expira

    salvar_usuarios(usuarios)

def tem_acesso(user_id):
    usuarios = carregar_usuarios()

    if str(user_id) not in usuarios:
        return False

    if usuarios[str(user_id)] == 9999999999:
        return True

    return time.time() < usuarios[str(user_id)]

# =============================
# INTERESSE
# =============================

def salvar_interesse(user_id):
    data = {}
    if os.path.exists(INTERESSE_FILE):
        with open(INTERESSE_FILE, "r") as f:
            data = json.load(f)

    data[str(user_id)] = int(time.time())

    with open(INTERESSE_FILE, "w") as f:
        json.dump(data, f)

def remover_interesse(user_id):
    if not os.path.exists(INTERESSE_FILE):
        return

    with open(INTERESSE_FILE, "r") as f:
        data = json.load(f)

    if str(user_id) in data:
        del data[str(user_id)]

    with open(INTERESSE_FILE, "w") as f:
        json.dump(data, f)

# =============================
# MARKETING
# =============================

nomes_fake = ["Lucas", "Marcos", "Ana", "Pedro", "Julia", "Rafael"]

def prova_social():
    return f"🔥 {random.choice(nomes_fake)} acabou de entrar no VIP"

def escassez():
    return f"⚠️ restam apenas {random.randint(3,9)} vagas hoje"

# =============================
# PLANOS
# =============================

PLANOS = {
    "isca": {"dias": 1, "preco": 5.00, "nome": "🔥 TESTE VIP 24H"},
    "1d": {"dias": 1, "preco": 7.00, "nome": "💰 1 DIA VIP"},
    "7d": {"dias": 7, "preco": 14.99, "nome": "🔥 7 DIAS VIP"},
    "15d": {"dias": 15, "preco": 22.99, "nome": "👑 15 DIAS VIP"},
    "pack": {"dias": 999, "preco": 10.99, "nome": "📦 BIBLIOTECA COMPLETA"}
}

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano):
    plano_info = PLANOS[plano]

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
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

    return r.json().get("init_point", "erro")

# =============================
# REMARKETING
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": f"{prova_social()}\n\n🔥 24h VIP por R$5\n{escassez()}\n\n👉 {link}"
        }
    )

    await asyncio.sleep(300)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": f"⏳ última chance\n\n{escassez()}\n\n👉 {link}"
        }
    )

# =============================
# START (COM FOTO)
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("😈 ENTRAR NO VIP", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption=
        "oii... tava te esperando aqui 🤭\n\n"
        "😈 tenho umas coisas que não posto em lugar nenhum...\n\n"
        "💦 e acho que você vai gostar",
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

        salvar_interesse(user_id)
        asyncio.create_task(remarketing(user_id))

        keyboard = [
            [InlineKeyboardButton("🔥 TESTE 24H R$5", callback_data="isca")],
            [InlineKeyboardButton("👑 15 DIAS R$22,99", callback_data="15d")],
            [InlineKeyboardButton("🔥 7 DIAS R$14,99", callback_data="7d")],
            [InlineKeyboardButton("💰 1 DIA R$7", callback_data="1d")],
            [InlineKeyboardButton("📦 COMPLETO R$10,99", callback_data="pack")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption=
            f"{prova_social()}\n\n"
            "😈 você não deveria estar vendo isso...\n\n"
            "💦 conteúdo exclusivo\n"
            f"{escassez()}\n\n"
            "👇 entra enquanto dá:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        await query.message.reply_text("⏳ gerando acesso...")

        time.sleep(1.5)

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"{PLANOS[query.data]['nome']}\n\n👉 {link}"
        )

# =============================
# ENTREGA + UPSELL
# =============================

def enviar_vip(chat_id, plano):
    chat_id = int(chat_id)

    remover_interesse(chat_id)
    liberar_acesso(chat_id, PLANOS[plano]["dias"])

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "😈 acesso liberado"}
    )

    if plano in ["isca", "1d"]:
        link = criar_pagamento(chat_id, "15d")

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"🔥 upgrade especial\n{escassez()}\n👉 {link}"
            }
        )

def enviar_pack(chat_id):
    chat_id = int(chat_id)

    remover_interesse(chat_id)
    liberar_acesso(chat_id, 999)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "📦 vitalício liberado"}
    )

# =============================
# WEBHOOK MP
# =============================

pagamentos_processados = set()

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

                if plano == "pack":
                    enviar_pack(user_id)
                else:
                    enviar_vip(user_id, plano)

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
