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

# =============================
# PLANOS
# =============================

PLANOS = {
    "1d": {"dias": 1, "preco": 8.99},
    "7d": {"dias": 7, "preco": 14.99},
    "15d": {"dias": 15, "preco": 22.99}
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

    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

    try:
        r = requests.post(url, json=payload, headers=headers)
        data = r.json()
        return data.get("point_of_interaction", {}).get("transaction_data", {}).get("ticket_url")
    except:
        return None

# =============================
# FUNÇÃO DE ENVIO DE MÍDIA
# =============================

def enviar_midias(user_id):
    try:
        # FOTO 1
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={
                "chat_id": user_id,
                "photo": "https://SEU_LINK_1.jpg",
                "caption": "👀 Primeira prévia..."
            }
        )

        # VÍDEO 1
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={
                "chat_id": user_id,
                "video": "https://SEU_VIDEO_1.mp4",
                "caption": "🔥 Agora ficou interessante..."
            }
        )

        # FOTO 2
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={
                "chat_id": user_id,
                "photo": "https://SEU_LINK_2.jpg",
                "caption": "😈 Só melhora..."
            }
        )

    except Exception as e:
        print("ERRO AO ENVIAR MIDIA:", e)

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

    await update.message.reply_text(
        "🔞😈 Oii... tava te esperando 👀🔥\n\n"
        "Preparei um conteúdo que não posto em lugar nenhum... 🤫\n\n"
        "Só quem entra aqui vê... 💋\n\n"
        "⚠️ Conteúdo +18 proibido ⚠️\n\n"
        "👇 Escolhe o que você quer ver:",
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
        await query.message.reply_text(
            "👀🔥 Só pra você sentir o gostinho...\n\n"
            "😈 Isso aqui não é nem 10% do que tem lá dentro...\n\n"
            "💋 O resto tá no VIP 🔒🔥"
        )

    elif query.data == "vip":
        if is_vip(user_id):
            await query.message.reply_text(
                "🔓🔥 Agora sim...\n\n"
                "😈 Você tem acesso total...\n\n"
                "💋 Aproveita..."
            )
        else:
            await query.message.reply_text(
                "🔞🔒 O conteúdo completo tá no VIP 😈🔥\n\n"
                "👇 Escolhe um plano:"
            )

    elif query.data in PLANOS:
        link = criar_pagamento(user_id, query.data)

        if link:
            await query.message.reply_text(
                f"💰 Finaliza aqui:\n{link}"
            )
        else:
            await query.message.reply_text("Erro ao gerar pagamento.")

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

                dias = PLANOS[plano]["dias"]

                liberar_vip(user_id, dias)

                # Mensagem
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={
                        "chat_id": user_id,
                        "text": f"🔥 VIP liberado por {dias} dias!\n\n😈 Segura isso..."
                    }
                )

                # 👇 ENVIA AS MÍDIAS
                enviar_midias(user_id)

    except Exception as e:
        print("ERRO MP:", e)

    return "ok", 200

# =============================
# SET WEBHOOK
# =============================

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

set_webhook()
