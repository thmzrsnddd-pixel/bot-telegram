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
# PLANOS
# =============================

PLANOS = {
    "isca": {"dias": 1, "preco": 4.50, "nome": "🔥 PROMOÇÃO 24H"},
    "teste": {"dias": 1, "preco": 6.99, "nome": "💰 TESTE VIP"},
    "7d": {"dias": 7, "preco": 14.99, "nome": "🔥 7 DIAS"},
    "15d": {"dias": 15, "preco": 22.99, "nome": "👑 15 DIAS"},
    "pack": {"dias": 999, "preco": 10.99, "nome": "📦 COMPLETO"}
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
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        asyncio.create_task(remarketing(user_id))

        keyboard = [
            [InlineKeyboardButton("🔥 R$4,50", callback_data="isca")],
            [InlineKeyboardButton("💰 R$6,99", callback_data="teste")],
            [InlineKeyboardButton("🔥 7 dias", callback_data="7d")],
            [InlineKeyboardButton("👑 15 dias", callback_data="15d")],
            [InlineKeyboardButton("📦 completo", callback_data="pack")]
        ]

        await query.message.reply_text(
            "eu não devia te mostrar isso... 😈\n\n👇 escolhe:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:
        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            "👉 PAGAMENTO AQUI\n\n" + link
        )

# =============================
# ENTREGA
# =============================

def enviar_midias(chat_id):
    chat_id = int(chat_id)

    for foto in FOTOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": foto})

    for video in VIDEOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": video})

# =============================
# LIBERAR (SÓ PRA VOCÊ)
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = update.effective_user.id

    try:
        enviar_midias(user_id)
        await update.message.reply_text("✅ mídias enviadas pra você")

    except Exception as e:
        await update.message.reply_text(f"❌ erro: {e}")

# =============================
# REMARKETING
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": f"🔥 promoção R$4,50\n\n👉 {link}"
        }
    )

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
            enviar_midias(user_id)

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

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("liberar", liberar))
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
