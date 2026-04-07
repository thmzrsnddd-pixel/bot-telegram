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

# =============================
# CONFIG
# =============================

TOKEN = "SEU_TOKEN_AQUI"
PUBLIC_URL = "https://seu-app.onrender.com"
MP_ACCESS_TOKEN = "SEU_MP_TOKEN"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# DIGITANDO
# =============================

def digitando(chat_id, tempo=2):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"}
    )
    time.sleep(tempo)

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
# MIDIAS
# =============================

FOTO_START = "SUA_FOTO_ID"
VIDEO_VIP = "SEU_VIDEO_ID"

MIDIAS_VIP = [
    {"tipo": "foto", "id": "ID1"},
    {"tipo": "foto", "id": "ID2"},
    {"tipo": "video", "id": "ID3"},
]

PACK_COMPLETO = MIDIAS_VIP

# =============================
# CONTROLE
# =============================

pagamentos_processados = set()

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
            "items": [
                {
                    "title": plano_info["nome"],
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": plano_info["preco"]
                }
            ],
            "external_reference": f"{user_id}|{plano}"
        }
    )

    return r.json().get("init_point", "Erro ao gerar pagamento")

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    keyboard = [
        [InlineKeyboardButton("🔒 ENTRAR NO VIP", callback_data="vip")]
    ]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption="oi... não sei se devia te responder aqui 😳\n\nfiquei meio sem graça...",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    digitando(user_id, 2)

    await update.message.reply_text(
        "🙈 normalmente não faço isso...\n\nmas você chamou minha atenção...\n\n💋 posso te mostrar um pouco..."
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "vip":

        digitando(user_id, 2)

        keyboard = [
            [InlineKeyboardButton("🔥 TESTE R$5", callback_data="isca")],
            [InlineKeyboardButton("💰 1 DIA R$7", callback_data="1d")],
            [InlineKeyboardButton("🔥 7 DIAS R$14,99", callback_data="7d")],
            [InlineKeyboardButton("👑 15 DIAS R$22,99", callback_data="15d")],
            [InlineKeyboardButton("📦 PACK COMPLETO R$10,99", callback_data="pack")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption="😈 aqui já é mais pessoal...\n\nescolhe como quer me ver...",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        digitando(user_id, 2)

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"💰 {PLANOS[query.data]['nome']}\n\n"
            f"👉 {link}\n\n"
            "assim que confirmar eu te libero 😳"
        )

# =============================
# RESPOSTAS AUTOMÁTICAS
# =============================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    digitando(user_id, 1)

    await update.message.reply_text(
        "🙈 você me deixa sem jeito...\n\nmas continua falando comigo..."
    )

# =============================
# ENTREGA VIP
# =============================

def enviar_vip(chat_id):

    chat_id = int(chat_id)

    digitando(chat_id, 2)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "😈 vou liberar um pouco pra você..."}
    )

    for midia in MIDIAS_VIP:
        if midia["tipo"] == "foto":
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={"chat_id": chat_id, "photo": midia["id"]})
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={"chat_id": chat_id, "video": midia["id"]})

# =============================
# ENTREGA PACK
# =============================

def enviar_pack(chat_id):

    chat_id = int(chat_id)

    digitando(chat_id, 2)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "📦 liberando biblioteca completa... aproveita 😈"}
    )

    for midia in PACK_COMPLETO:
        if midia["tipo"] == "foto":
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={"chat_id": chat_id, "photo": midia["id"]})
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={"chat_id": chat_id, "video": midia["id"]})

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
                user_id = int(user_id)

                if plano == "pack":
                    enviar_pack(user_id)
                else:
                    enviar_vip(user_id)

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
    return "online", 200

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

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
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
