from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os

# =============================
# CONFIG
# =============================

TOKEN = "SEU_TOKEN_AQUI"
PUBLIC_URL = "SEU_RENDER_URL"
MP_ACCESS_TOKEN = "SEU_MP_TOKEN"
ADMIN_ID = 8584498503

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios_funil = set()
usuarios_upsell = set()

# =============================
# MIDIAS
# =============================

FOTO_START = "SEU_FILE_ID"

FOTOS = ["ID1","ID2"]
VIDEOS = ["ID1","ID2"]

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

def criar_pix(user_id, plano):
    plano_info = PLANOS[plano]

    r = requests.post(
        "https://api.mercadopago.com/v1/payments",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "transaction_amount": plano_info["preco"],
            "payment_method_id": "pix",
            "description": plano_info["nome"],
            "payer": {"email": f"user{user_id}@teste.com"},
            "external_reference": f"{user_id}|{plano}"
        }
    ).json()

    return r

# =============================
# MIDIAS
# =============================

def enviar_fotos(chat_id):
    for f in FOTOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": chat_id, "photo": f})

def enviar_videos(chat_id):
    for v in VIDEOS:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                      json={"chat_id": chat_id, "video": v})

def enviar_preview(chat_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                  json={"chat_id": chat_id, "video": VIDEOS[0]})

# =============================
# FUNIL
# =============================

async def funil(user_id):
    await asyncio.sleep(120)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "ei... saiu assim? 😏"})

    await asyncio.sleep(480)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": user_id, "text": "tem coisa ali que eu não mostro sempre 👀"})

    await asyncio.sleep(1200)

    link = criar_pagamento(user_id, "isca")

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": "última chance 😈\n\nte libero por R$4,50 👇",
            "reply_markup": {"inline_keyboard": [[{"text": "🔥 ENTRAR", "url": link}]]}
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
        caption="oii... entra 😈",
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

        await query.message.reply_text("escolhe 😈", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in PLANOS:
        pix = criar_pix(user_id, query.data)
        link = criar_pagamento(user_id, query.data)

        pix_code = pix.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code", "erro")

        await query.message.reply_text(
            f"💳 PIX:\n\n{pix_code}\n\nou paga aqui 👇\n{link}"
        )

# =============================
# LIBERAR (ADMIN)
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    enviar_fotos(ADMIN_ID)
    enviar_videos(ADMIN_ID)
    await update.message.reply_text("✅ enviado")

# =============================
# MP WEBHOOK
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

            elif plano == "upgrade":
                enviar_videos(user_id)

            elif plano == "leve":
                enviar_fotos(user_id)

            elif plano == "pesado":
                enviar_videos(user_id)

            else:
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
bot_app.add_handler(CommandHandler("liberar", liberar))
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
