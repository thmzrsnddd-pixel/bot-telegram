from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"
ADMIN_ID = 8584498503

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios_funil = set()
usuarios_upsell = set()

# =============================
# MIDIAS
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
"BAACAgEAAxkBAAIDPWnWqNtgenHSZrHn6qLFSdzOW-tNAAJKCAAC9KC4RrM2wJoZDWpWOwQ"
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

# =============================
# ENVIO MIDIAS
# =============================

def enviar_fotos(chat_id):
    for foto in FOTOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": foto})

def enviar_videos(chat_id):
    for video in VIDEOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": video})

def enviar_preview(chat_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                  json={"chat_id": chat_id, "video": VIDEOS[0]})

# =============================
# FUNIL AUTOMATICO
# =============================

async def funil(user_id):
    await asyncio.sleep(120)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "ei... saiu assim? 😏"})

    await asyncio.sleep(480)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "tem coisa ali que eu não mostro sempre não 👀"})

    await asyncio.sleep(1200)
    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": "última chance 😈\n\nte libero por R$4,50 👇",
            "reply_markup": {"inline_keyboard": [[{"text": "🔥 ENTRAR AGORA", "url": link}]]}
        })

# =============================
# UPSELL REMARKETING
# =============================

async def upsell_remarketing(user_id):
    await asyncio.sleep(300)

    if user_id in usuarios_upsell:
        return

    link = criar_pagamento(user_id, "upgrade")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": "👀 ainda ta ai?\n\nlibero o resto por R$3,99 👇",
            "reply_markup": {"inline_keyboard": [[{"text": "🔓 LIBERAR", "url": link}]]}
        })

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in usuarios_funil:
        usuarios_funil.add(user_id)
        asyncio.create_task(funil(user_id))

    keyboard = [[InlineKeyboardButton("😈 entrar", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption="oii... 🤭\n\nentra se tiver coragem 😈",
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

        await query.message.reply_text(
            "eu separei por níveis... 😈\n\n👇 escolhe:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:
        link = criar_pagamento(user_id, query.data)
        await query.message.reply_text("😏 boa escolha...\n\n👇\n" + link)

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

            if plano == "isca":
                enviar_fotos(user_id)
                enviar_preview(user_id)

                link = criar_pagamento(user_id, "upgrade")

                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={
                        "chat_id": user_id,
                        "text": "😈 quer liberar tudo?\n\nsó R$3,99 👇",
                        "reply_markup": {"inline_keyboard": [[{"text": "🔓 LIBERAR", "url": link}]]}
                    })

                asyncio.create_task(upsell_remarketing(user_id))

            elif plano == "upgrade":
                usuarios_upsell.add(user_id)
                enviar_videos(user_id)

            elif plano == "leve":
                enviar_fotos(user_id)

                link = criar_pagamento(user_id, "pesado")

                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={
                        "chat_id": user_id,
                        "text": "😈 quer subir pro PESADO por +R$4,99? 👇",
                        "reply_markup": {"inline_keyboard": [[{"text": "🔥 SUBIR", "url": link}]]}
                    })

            elif plano == "pesado":
                enviar_videos(user_id)

                link = criar_pagamento(user_id, "pesadissimo")

                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={
                        "chat_id": user_id,
                        "text": "💀 agora o PESADÍSSIMO por +R$4,99 👇",
                        "reply_markup": {"inline_keyboard": [[{"text": "💀 SUBIR", "url": link}]]}
                    })

            elif plano == "pesadissimo":
                enviar_fotos(user_id)
                enviar_videos(user_id)

            elif plano == "pack":
                enviar_fotos(user_id)
                enviar_videos(user_id)

    return "ok", 200

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)

    asyncio.run(bot_app.initialize())
    asyncio.run(bot_app.process_update(update))

    return "ok"

@app.route("/")
def home():
    return "online"

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

set_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
