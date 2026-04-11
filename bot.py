from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import base64
import time
import json

# =============================
# CONFIG
# =============================

TOKEN = "SEU_TOKEN"
PUBLIC_URL = "SEU_URL"
MP_ACCESS_TOKEN = "SEU_MP"
ADMIN_ID = 8584498503

app = Flask(__name__)

bot_app = ApplicationBuilder().token(TOKEN).build()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(bot_app.initialize())

usuarios_funil = set()

# 🔒 ARQUIVO PRA BLOQUEAR DUPLICAÇÃO
ARQUIVO_PAGAMENTOS = "pagamentos.json"

if not os.path.exists(ARQUIVO_PAGAMENTOS):
    with open(ARQUIVO_PAGAMENTOS, "w") as f:
        json.dump([], f)

def ja_processado(payment_id):
    with open(ARQUIVO_PAGAMENTOS, "r") as f:
        data = json.load(f)
    return payment_id in data

def salvar_processado(payment_id):
    with open(ARQUIVO_PAGAMENTOS, "r") as f:
        data = json.load(f)

    data.append(payment_id)

    with open(ARQUIVO_PAGAMENTOS, "w") as f:
        json.dump(data, f)

# =============================
# MIDIAS
# =============================

FOTOS = [ ... SEUS IDS AQUI ... ]
VIDEOS = [ ... SEUS IDS AQUI ... ]

def enviar_fotos(chat_id):
    for foto in FOTOS:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": foto}
        )
        time.sleep(1)

def enviar_videos(chat_id):
    for video in VIDEOS:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": video}
        )
        time.sleep(1.5)

# =============================
# WEBHOOK MP (BLINDADO)
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    if data.get("type") == "payment":
        payment_id = str(data["data"]["id"])

        # 🔒 BLOQUEIO FORTE
        if ja_processado(payment_id):
            return "ok", 200

        pagamento = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        ).json()

        if pagamento.get("status") == "approved":

            salvar_processado(payment_id)

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
# RESTO DO BOT (mantém igual)
# =============================

@app.route("/")
def home():
    return "online"

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

set_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
