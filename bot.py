from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import asyncio
import requests
import os
import time

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
# BANCO SIMPLES (MEMÓRIA)
# =============================

usuarios = {}

def registrar(user_id):
    if user_id not in usuarios:
        usuarios[user_id] = {
            "entrou": time.time(),
            "clicou": None,
            "comprou": False
        }

# =============================
# MIDIAS
# =============================

FOTO_START = "AgACAgEAAyEFAATanvxOAAMfadalWki1wP7-1YvoJzGG9b_SDb4AAiQMaxtbAAG5Rm_IZa1EkJk2AQADAgADeQADOwQ"

FOTOS_LEVE = [
"AgACAgEAAyEFAATanvxOAAMgadalWpQu9iHfYUWKgZ7DtzZRqI8AAicMaxtbAAG5RiyZJaeK4ptQAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMhadalWk1MTJUd0pkxCyGvSG3_UfYAAiUMaxtbAAG5RkRVtVGrJj0DAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMiadalWqyrO-DiYl9D6juKlr5epIYAAiYMaxtbAAG5Rhow-8sHdlnOAQADAgADeQADOwQ"
]

VIDEOS_PESADO = [
"BAACAgEAAxkBAAIDOWnWqNs-1FpAl43ilynlUwZ0g6g8AAJICAAC9KC4Rh5FmcPCMztcOwQ",
"BAACAgEAAxkBAAIDOmnWqNv51sHmOSI4skR7Leg_niGDAAJACAAC9KC4RoWPxz3SVNSNOwQ"
]

TODOS = FOTOS_LEVE + VIDEOS_PESADO

# =============================
# PLANOS
# =============================

PLANOS = {
    "leve": {"preco": 5.00},
    "pesado": {"preco": 8.99},
    "pesadissimo": {"preco": 12.99},
    "completo": {"preco": 15.99}
}

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano, extra=0):
    preco = PLANOS[plano]["preco"] + extra

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
        json={
            "items": [{
                "title": plano,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco
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

    keyboard = [[InlineKeyboardButton("😈 Quero entrar", callback_data="vip")]]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption="👀 opa...\n\nacho que você não devia estar aqui...\n\nmas já que veio...\n👇",
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

        asyncio.create_task(remarketing(user_id))

        keyboard = [
            [InlineKeyboardButton("😈 Só curiosidade", callback_data="leve")],
            [InlineKeyboardButton("🔥 Quero mais", callback_data="pesado")],
            [InlineKeyboardButton("👑 Sem limites", callback_data="pesadissimo")],
            [InlineKeyboardButton("💎 Quero tudo", callback_data="completo")]
        ]

        await query.message.reply_text(
            "😏 até onde você vai aguentar?\n\n(escolhe com cuidado...)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        usuarios[user_id]["clicou"] = query.data

        # ISCA REAL
        await query.message.reply_text("👀 calma...\n\nvou te mostrar só um gostinho primeiro...")

        await asyncio.sleep(2)

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": user_id, "photo": FOTOS_LEVE[0]})

        await asyncio.sleep(2)

        link = criar_pagamento(user_id, query.data)

        keyboard = [[InlineKeyboardButton("😈 desbloquear agora", url=link)]]

        await query.message.reply_text(
            "😳 agora imagina o resto...\n\n👇 libera aqui:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# ENTREGA + DELAY + UPSELL
# =============================

def enviar_leve(chat_id):
    for foto in FOTOS_LEVE:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": foto})
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesado", 3.99)

    keyboard = [[{"text": "🔥 subir nível (+3,99)", "url": link}]]

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "😳 gostou?\n\nisso foi só o começo...",
              "reply_markup": {"inline_keyboard": keyboard}})

def enviar_pesado(chat_id):
    for video in VIDEOS_PESADO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": video})
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesadissimo", 3.99)

    keyboard = [[{"text": "👑 ir pro máximo (+3,99)", "url": link}]]

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "😈 agora ficou sério...",
              "reply_markup": {"inline_keyboard": keyboard}})

def enviar_pesadissimo(chat_id):
    for midia in TODOS:
        if midia.startswith("Ag"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          json={"chat_id": chat_id, "photo": midia})
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                          json={"chat_id": chat_id, "video": midia})
        time.sleep(1)

    link = criar_pagamento(chat_id, "completo", 3.00)

    keyboard = [[{"text": "💎 liberar tudo (+3,00)", "url": link}]]

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "👑 quase tudo liberado...",
              "reply_markup": {"inline_keyboard": keyboard}})

def enviar_completo(chat_id):
    enviar_pesadissimo(chat_id)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "💎 acesso total liberado 😈"})

# =============================
# REMARKETING INTELIGENTE
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    plano = usuarios[user_id]["clicou"]

    if not plano:
        return

    link = criar_pagamento(user_id, plano)

    keyboard = [[{"text": "😈 voltar agora", "url": link}]]

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id,
              "text": f"👀 vi que você quase pegou o {plano}...\n\nficou com medo? 😏",
              "reply_markup": {"inline_keyboard": keyboard}})

# =============================
# LOG DE VENDAS
# =============================

def avisar_admin(texto):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": ADMIN_ID, "text": texto})

# =============================
# LIBERAR ADMIN
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    plano = context.args[0]

    if plano == "leve":
        enviar_leve(update.message.chat_id)
    elif plano == "pesado":
        enviar_pesado(update.message.chat_id)
    elif plano == "pesadissimo":
        enviar_pesadissimo(update.message.chat_id)
    elif plano == "completo":
        enviar_completo(update.message.chat_id)

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

            usuarios[user_id]["comprou"] = True

            avisar_admin(f"💰 venda: {plano}")

            if plano == "leve":
                enviar_leve(user_id)
            elif plano == "pesado":
                enviar_pesado(user_id)
            elif plano == "pesadissimo":
                enviar_pesadissimo(user_id)
            elif plano == "completo":
                enviar_completo(user_id)

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
