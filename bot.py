from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import requests
import time
import json
import os
import threading

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

ADMIN_ID = 8584498503  # ⚠️ coloca seu ID aqui

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

DB_FILE = "usuarios.json"
INTERESSE_FILE = "interesse.json"

# =============================
# MIDIA
# =============================

FOTO_START = "AgACAgEAAxkBAAIBW2nVAAHA4MmTOu-BxgLp5jg8Ki_BSwACGAxrG6ZgqUZa618MB7ra7wEAAwIAA3kAAzsE"
VIDEO_VIP = "BAACAgEAAyEFAATanvxOAAMUadUHHCYG4cpssnNLzoS_9tzrQAgAAvoHAAKmYKlGY1cOvM0Wqzw7BA"

MIDIAS_VIP = [
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXGnVAAHAb5B3BdUxiosov-1dgCmJKwACFwxrG6ZgqUaMyF1kSngZSgEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXWnVAAHAbVGKwRoQSJjZ3BNnHh7NqQACGQxrG6ZgqUbCJc8OBDvJYwEAAwIAA3kAAzsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBYmnVAAHAeHwHLWHdbsLbnNUvLIaoVgAC8QcAAqZgqUbtoS5YWN_WPjsE"},
]

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

def carregar_interesse():
    if not os.path.exists(INTERESSE_FILE):
        return {}
    with open(INTERESSE_FILE, "r") as f:
        return json.load(f)

def salvar_interesse(user_id):
    data = carregar_interesse()
    data[str(user_id)] = {
        "tempo": int(time.time()),
        "enviado": False
    }
    with open(INTERESSE_FILE, "w") as f:
        json.dump(data, f)

def remover_interesse(user_id):
    data = carregar_interesse()
    if str(user_id) in data:
        del data[str(user_id)]
    with open(INTERESSE_FILE, "w") as f:
        json.dump(data, f)

# =============================
# PLANOS
# =============================

PLANOS = {
    "isca": {"dias": 1, "preco": 4.50, "nome": "🔥 TESTE VIP 24H"},
    "1d": {"dias": 1, "preco": 7.00, "nome": "💰 1 DIA VIP"},
    "7d": {"dias": 7, "preco": 14.99, "nome": "🔥 7 DIAS VIP"},
    "15d": {"dias": 15, "preco": 22.99, "nome": "👑 15 DIAS VIP"},
    "pack": {"dias": 999, "preco": 10.99, "nome": "📦 COMPLETO"}
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
# REMARKETING AUTOMÁTICO
# =============================

def loop_remarketing():
    while True:
        try:
            data = carregar_interesse()
            agora = int(time.time())

            for user_id, info in data.items():
                user_id = int(user_id)

                if tem_acesso(user_id):
                    continue

                if info["enviado"]:
                    continue

                if agora - info["tempo"] > 120:
                    link = criar_pagamento(user_id, "isca")

                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        json={
                            "chat_id": user_id,
                            "text":
                            "ei... você sumiu 😔\n\n"
                            "te libero 24h por R$4,50 agora...\n\n"
                            f"{link}"
                        }
                    )

                    data[str(user_id)]["enviado"] = True

            with open(INTERESSE_FILE, "w") as f:
                json.dump(data, f)

        except Exception as e:
            print("ERRO LOOP:", e)

        time.sleep(60)

threading.Thread(target=loop_remarketing, daemon=True).start()

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("😈 entrar", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption=
        "oii... 🤭\n\n"
        "acho que você não devia estar aqui 😈",
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

        keyboard = [
            [InlineKeyboardButton("🔥 teste R$4,50", callback_data="isca")],
            [InlineKeyboardButton("👑 15 dias", callback_data="15d")],
            [InlineKeyboardButton("🔥 7 dias", callback_data="7d")],
            [InlineKeyboardButton("💰 1 dia", callback_data="1d")],
            [InlineKeyboardButton("📦 completo", callback_data="pack")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption="👇 escolhe e entra",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(f"{link}")

# =============================
# ENTREGA (ANTI PRINT)
# =============================

def enviar_vip(chat_id, plano):
    chat_id = int(chat_id)

    remover_interesse(chat_id)
    liberar_acesso(chat_id, PLANOS[plano]["dias"])

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": f"🔒 acesso liberado\nID: {chat_id}\nnão compartilha"
        }
    )

    for midia in MIDIAS_VIP:
        time.sleep(2)

        if midia["tipo"] == "foto":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={
                    "chat_id": chat_id,
                    "photo": midia["id"],
                    "protect_content": True
                }
            )

        elif midia["tipo"] == "video":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                json={
                    "chat_id": chat_id,
                    "video": midia["id"],
                    "protect_content": True
                }
            )

def enviar_pack(chat_id):
    enviar_vip(chat_id, "pack")

# =============================
# COMANDO TESTE
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = update.effective_chat.id

    enviar_vip(user_id, "1d")

    await update.message.reply_text("liberado para teste")

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

    import asyncio
    asyncio.run(process())

    return "ok", 200

@app.route("/")
def home():
    return "online", 200

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
