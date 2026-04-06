from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIP_FILE = os.path.join(BASE_DIR, "vip.json")

loop = asyncio.get_event_loop()

# =============================
# PLANOS
# =============================

PLANOS = {
    "1d": {"dias": 1, "preco": 10},
    "7d": {"dias": 7, "preco": 20},
    "15d": {"dias": 15, "preco": 30}
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
    user_id = str(user_id)
    if user_id in usuarios_vip:
        return time.time() < usuarios_vip[user_id]
    return False

def liberar_vip(user_id, dias):
    user_id = str(user_id)
    tempo = dias * 86400
    usuarios_vip[user_id] = time.time() + tempo
    salvar_vip(usuarios_vip)

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

    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    print("MP:", data)

    return data.get("point_of_interaction", {}).get("transaction_data", {}).get("ticket_url")

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia", callback_data="previa")],
        [InlineKeyboardButton("🔒 VIP", callback_data="vip")],
        [InlineKeyboardButton("💰 1 DIA", callback_data="1d")],
        [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
        [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")]
    ]

    with open(os.path.join(BASE_DIR, "foto1.jpg"), "rb") as foto:
        await update.message.reply_photo(
            photo=foto,
            caption="😈 Conteúdo exclusivo 👇",
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
            await query.message.reply_photo(photo=foto, caption="👀 Prévia")

    elif query.data == "vip":
        if is_vip(user_id):
            with open(os.path.join(BASE_DIR, "video1.mp4"), "rb") as video:
                await query.message.reply_video(video=video, caption="🔥 VIP liberado")
        else:
            await query.message.reply_text("🔒 Compre um plano")

    elif query.data in PLANOS:
        link = criar_pagamento(user_id, query.data)

        if link:
            await query.message.reply_text(f"💰 Pague aqui:\n{link}")
        else:
            await query.message.reply_text("❌ Erro ao gerar pagamento")

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# ROTA HOME (IMPORTANTE)
# =============================

@app.route("/", methods=["GET"])
def home():
    return "BOT ONLINE", 200

# =============================
# WEBHOOK TELEGRAM (CORRIGIDO)
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)

    asyncio.run_coroutine_threadsafe(
        bot_app.process_update(update),
        loop
    )

    return "ok", 200

# =============================
# WEBHOOK MERCADO PAGO
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    try:
        if data.get("type") == "payment" or data.get("topic") == "payment":
            payment_id = data["data"]["id"]

            r = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
            )

            pagamento = r.json()

            if pagamento.get("status") == "approved":
                ref = pagamento.get("external_reference")

                if ref and "|" in ref:
                    user_id, plano = ref.split("|")

                    dias = PLANOS[plano]["dias"]
                    liberar_vip(user_id, dias)

                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        json={
                            "chat_id": user_id,
                            "text": f"🔥 VIP liberado por {dias} dias!"
                        }
                    )

    except Exception as e:
        print("ERRO MP:", e)

    return "ok", 200

# =============================
# START BOT (CORRETO)
# =============================

async def iniciar():
    await bot_app.initialize()

loop.run_until_complete(iniciar())

# =============================
# SET WEBHOOK
# =============================

requests.get(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
)
