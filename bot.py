from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import requests
import os
import time

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"
ADMIN_ID = 8584498503

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios = {}

def registrar(user_id):
    if user_id not in usuarios:
        usuarios[user_id] = {"clicou": None, "comprou": False}

# =============================
# MIDIAS
# =============================

FOTOS_LEVE = [
"AgACAgEAAyEFAATanvxOAAMfadalWki1wP7-1YvoJzGG9b_SDb4AAiQMaxtbAAG5Rm_IZa1EkJk2AQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMgadalWpQu9iHfYUWKgZ7DtzZRqI8AAicMaxtbAAG5RiyZJaeK4ptQAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMhadalWk1MTJUd0pkxCyGvSG3_UfYAAiUMaxtbAAG5RkRVtVGrJj0DAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMiadalWqyrO-DiYl9D6juKlr5epIYAAiYMaxtbAAG5Rhow-8sHdlnOAQADAgADeQADOwQ"
]

VIDEOS_PESADO = [
"BAACAgEAAxkBAAIDOWnWqNs-1FpAl43ilynlUwZ0g6g8AAJICAAC9KC4Rh5FmcPCMztcOwQ",
"BAACAgEAAxkBAAIDOmnWqNv51sHmOSI4skR7Leg_niGDAAJACAAC9KC4RoWPxz3SVNSNOwQ"
]

PLANOS = {
    "leve": 5.00,
    "pesado": 8.99,
    "pesadissimo": 12.99,
    "completo": 15.99
}

def criar_pagamento(user_id, plano):
    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
        json={
            "items": [{
                "title": plano,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": PLANOS[plano]
            }],
            "external_reference": f"{user_id}|{plano}"
        }
    )
    return r.json().get("init_point")

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    registrar(user_id)

    keyboard = [[InlineKeyboardButton("😈 Entrar", callback_data="vip")]]

    await update.message.reply_text(
        "👀 você encontrou isso por acaso...\n\nclica aí 😏",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    registrar(user_id)

    if query.data == "vip":
        keyboard = [
            [InlineKeyboardButton("😈 leve", callback_data="leve")],
            [InlineKeyboardButton("🔥 pesado", callback_data="pesado")],
            [InlineKeyboardButton("👑 máximo", callback_data="pesadissimo")]
        ]

        await query.message.reply_text("escolhe aí 😏", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in PLANOS:
        usuarios[user_id]["clicou"] = query.data

        link = criar_pagamento(user_id, query.data)

        keyboard = [[InlineKeyboardButton("😈 pagar", url=link)]]

        await query.message.reply_text(
            "😏 desbloqueia aqui:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# WEBHOOK TELEGRAM (CORRIGIDO)
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.get_event_loop().run_until_complete(bot_app.process_update(update))
    return "ok"

# =============================
# RUN
# =============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
