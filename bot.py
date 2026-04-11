from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import base64
import time
import json
import threading

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

# =============================
# ANTI DUPLICAÇÃO
# =============================

ARQUIVO = "pagamentos.json"

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump([], f)

def ja_processado(pid):
    with open(ARQUIVO, "r") as f:
        return pid in json.load(f)

def salvar(pid):
    with open(ARQUIVO, "r") as f:
        data = json.load(f)

    data.append(pid)

    with open(ARQUIVO, "w") as f:
        json.dump(data, f)

# =============================
# MIDIAS (TODAS)
# =============================

FOTOS = [
"AgACAgEAAyEFAATanvxOAAMgadalWpQu9iHfYUWKgZ7DtzZRqI8AAicMaxtbAAG5RiyZJaeK4ptQAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMhadalWk1MTJUd0pkxCyGvSG3_UfYAAiUMaxtbAAG5RkRVtVGrJj0DAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMiadalWqyrO-DiYl9D6juKlr5epIYAAiYMaxtbAAG5Rhow-8sHdlnOAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMjadalWufKeZ_A5IqW1lU9BiCmPjEAAigMaxtbAAG5Rh_43jcPh2SPAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMkadalWvazoCPw5Wl8X-8IJgF9cR8AAioMaxtbAAG5RiaHphVTp9iZAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMladalWhXgdDnrD-tUwoTyInpEKMIAAikMaxtbAAG5RgV6iGNg7W5PAQADAgADeQADOwQ"
]

VIDEOS = [
"BAACAgEAAxkBAAIDOWnWqNs-1FpAl43ilynlUwZ0g6g8AAJICAAC9KC4Rh5FmcPCMztcOwQ",
"BAACAgEAAxkBAAIDOmnWqNv51sHmOSI4skR7Leg_niGDAAJACAAC9KC4RoWPxz3SVNSNOwQ",
"BAACAgEAAxkBAAIDO2nWqNujS8IkK5L9bnaBzeNpQqjfAAJGCAAC9KC4RhGwOQG7fi2xOwQ",
"BAACAgEAAxkBAAIDPGnWqNvwfsAZSsn_S8RvVLvcHNM9AAJOCAAC9KC4RmN0c2OjuTyaOwQ",
"BAACAgEAAxkBAAIDPWnWqNtgenHSZrHn6qLFSdzOW-tNAAJKCAAC9KC4RrM2wJoZDWpWOwQ",
"BAACAgEAAxkBAAIDPmnWqNtDzi5ZnGSDbD9Wjmf2dnHDAAJCCAAC9KC4Rj5Z_R4Jd3PNOwQ",
"BAACAgEAAxkBAAIDP2nWqNuzpCpLt63s0xflUxkwj5PxAAJPCAAC9KC4RvNRz2QkIt0gOwQ",
"BAACAgEAAxkBAAIDQGnWqNsope1o0KEPsiF-E8oybrkMAAJMCAAC9KC4RtFnuxv8mNjeOwQ",
"BAACAgEAAxkBAAIDQWnWqNt16VBbSZ4HB-T8JdnUsi9HAAJHCAAC9KC4Rl2bdgy3ggfzOwQ",
"BAACAgEAAxkBAAIDQmnWqNvFhIE23xwDLCxaSu7GBDKnAAJDCAAC9KC4Ru6UCoGAN02NOwQ",
"BAACAgEAAxkBAAIDQ2nWqNuh23ry1SLL0DzdlLnKN9QrAAJFCAAC9KC4RtQY7wGiIsYFOwQ",
"BAACAgEAAxkBAAIDRGnWqNs5349OAsmFsFk0bzhNI5t6AAJJCAAC9KC4Ri7Tie6IGxBfOwQ",
"BAACAgEAAxkBAAIDRWnWqNsTztM9iJT_xH-766GRMWQeAAJNCAAC9KC4RgbUOhCNs0LGOwQ",
"BAACAgEAAxkBAAIDRmnWqNvIk0GV0051QxjuXQjTDVLIAAJBCAAC9KC4RiJEk_m4MDL3OwQ"
]

# =============================
# ENVIO EM BACKGROUND
# =============================

def liberar_conteudo(user_id, plano):
    if plano == "leve":
        for f in FOTOS:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          json={"chat_id": user_id, "photo": f})
            time.sleep(1)

    elif plano == "pesado":
        for v in VIDEOS:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                          json={"chat_id": user_id, "video": v})
            time.sleep(1.5)

    else:
        for f in FOTOS:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          json={"chat_id": user_id, "photo": f})
            time.sleep(1)

        for v in VIDEOS:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                          json={"chat_id": user_id, "video": v})
            time.sleep(1.5)

# =============================
# WEBHOOK MP (CORRETO)
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    if data.get("type") == "payment":
        payment_id = str(data["data"]["id"])

        if ja_processado(payment_id):
            return "ok", 200

        salvar(payment_id)

        pagamento = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        ).json()

        if pagamento.get("status") == "approved":
            user_id, plano = pagamento["external_reference"].split("|")
            user_id = int(user_id)

            # 🚀 roda em background
            threading.Thread(target=liberar_conteudo, args=(user_id, plano)).start()

    return "ok", 200

# =============================
# RESTO
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
