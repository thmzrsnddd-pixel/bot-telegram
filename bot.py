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
import json
import os

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

pagamentos_processados = set()

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
        usuarios[str(user_id)] = int(time.time()) + dias * 86400

    salvar_usuarios(usuarios)

def tem_acesso(user_id):
    usuarios = carregar_usuarios()
    return str(user_id) in usuarios and (
        usuarios[str(user_id)] == 9999999999 or time.time() < usuarios[str(user_id)]
    )

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
# PLANOS
# =============================

PLANOS = {
    "isca": {"dias": 0, "preco": 5.00, "nome": "🔥 TESTE VIP"},
    "1d": {"dias": 1, "preco": 7.00, "nome": "💰 1 DIA VIP"},
    "7d": {"dias": 7, "preco": 14.99, "nome": "🔥 7 DIAS VIP"},
    "15d": {"dias": 15, "preco": 22.99, "nome": "👑 15 DIAS VIP"},
    "pack": {"dias": 999, "preco": 10.99, "nome": "📦 BIBLIOTECA COMPLETA"}
}

# =============================
# MIDIAS COMPLETAS
# =============================

FOTO_START = "AgACAgEAAyEFAATanvxOAAMfadalWki1wP7-1YvoJzGG9b_SDb4AAiQMaxtbAAG5Rm_IZa1EkJk2AQADAgADeQADOwQ"

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
# ENVIO
# =============================

def enviar_midias(chat_id):
    for foto in FOTOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": foto})
        time.sleep(0.4)

    for video in VIDEOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": video})
        time.sleep(0.6)

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

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("😈 entrar", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption="oii… 🤭\n\nnão devia te responder aqui...\n\nentra por sua conta 😈",
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
        asyncio.create_task(remarketing2(user_id))

        keyboard = [
            [InlineKeyboardButton("🔥 TESTE", callback_data="isca")],
            [InlineKeyboardButton("💰 1 DIA", callback_data="1d")],
            [InlineKeyboardButton("🔥 7 DIAS", callback_data="7d")],
            [InlineKeyboardButton("👑 15 DIAS", callback_data="15d")],
            [InlineKeyboardButton("📦 COMPLETO", callback_data="pack")]
        ]

        await query.message.reply_text(
            "😈 então você entrou mesmo...\n\nnão mostra isso pra ninguém\n\n👇 escolhe:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"😈 acesso liberado em segundos...\n\n⚠️ link expira rápido\n\n👉 {link}"
        )

# =============================
# ENTREGA
# =============================

def enviar_vip(chat_id, plano):
    liberar_acesso(chat_id, PLANOS[plano]["dias"])

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": "😈 segura... isso aqui não era pra qualquer um..."})

    time.sleep(2)

    enviar_midias(chat_id)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": "👀 quer ver o que eu não mando pra todo mundo?"})

    link = criar_pagamento(chat_id, "pack")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": f"🔥 tem coisa que não mandei aqui...\n\n👉 {link}"})

# =============================
# REMARKETING
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id,
              "text": f"😳 ei...\n\nvi que você entrou e saiu...\n\nvou liberar por pouco tempo\n\n👉 {link}"})

async def remarketing2(user_id):
    await asyncio.sleep(600)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id,
              "text": f"👀 apaguei quase tudo...\n\nsobrou isso aqui\n\n👉 {link}"})

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
                enviar_vip(int(user_id), plano)

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
    return "online"

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None))

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
