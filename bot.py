from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
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
# WEBHOOK
# =============================

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": f"{PUBLIC_URL}/webhook/{TOKEN}"}
    )

set_webhook()

# =============================
# BANCO
# =============================

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

FOTOS_PESADO = [
"AgACAgEAAyEFAATanvxOAAMjadalWufKeZ_A5IqW1lU9BiCmPjEAAigMaxtbAAG5Rh_43jcPh2SPAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMkadalWvazoCPw5Wl8X-8IJgF9cR8AAioMaxtbAAG5RiaHphVTp9iZAQADAgADeQADOwQ",
"AgACAgEAAyEFAATanvxOAAMladalWhXgdDnrD-tUwoTyInpEKMIAAikMaxtbAAG5RgV6iGNg7W5PAQADAgADeQADOwQ"
]

VIDEOS_PESADO = [
"BAACAgEAAxkBAAIDOWnWqNs-1FpAl43ilynlUwZ0g6g8AAJICAAC9KC4Rh5FmcPCMztcOwQ",
"BAACAgEAAxkBAAIDOmnWqNv51sHmOSI4skR7Leg_niGDAAJACAAC9KC4RoWPxz3SVNSNOwQ",
"BAACAgEAAxkBAAIDO2nWqNujS8IkK5L9bnaBzeNpQqjfAAJGCAAC9KC4RhGwOQG7fi2xOwQ",
"BAACAgEAAxkBAAIDPGnWqNvwfsAZSsn_S8RvVLvcHNM9AAJOCAAC9KC4RmN0c2OjuTyaOwQ"
]

VIDEOS_PESADISSIMO = [
"BAACAgEAAxkBAAIDPWnWqNtgenHSZrHn6qLFSdzOW-tNAAJKCAAC9KC4RrM2wJoZDWpWOwQ",
"BAACAgEAAxkBAAIDPmnWqNtDzi5ZnGSDbD9Wjmf2dnHDAAJCCAAC9KC4Rj5Z_R4Jd3PNOwQ",
"BAACAgEAAxkBAAIDP2nWqNuzpCpLt63s0xflUxkwj5PxAAJPCAAC9KC4RvNRz2QkIt0gOwQ",
"BAACAgEAAxkBAAIDQGnWqNsope1o0KEPsiF-E8oybrkMAAJMCAAC9KC4RtFnuxv8mNjeOwQ",
"BAACAgEAAxkBAAIDQWnWqNt16VBbSZ4HB-T8JdnUsi9HAAJHCAAC9KC4Rl2bdgy3ggfzOwQ",
"BAACAgEAAxkBAAIDQmnWqNvFhIE23xwDLCxaSu7GBDKnAAJDCAAC9KC4Ru6UCoGAN02NOwQ"
]

VIDEOS_COMPLETO = [
"BAACAgEAAxkBAAIDQ2nWqNuh23ry1SLL0DzdlLnKN9QrAAJFCAAC9KC4RtQY7wGiIsYFOwQ",
"BAACAgEAAxkBAAIDRGnWqNs5349OAsmFsFk0bzhNI5t6AAJJCAAC9KC4Ri7Tie6IGxBfOwQ",
"BAACAgEAAxkBAAIDRWnWqNsTztM9iJT_xH-766GRMWQeAAJNCAAC9KC4RgbUOhCNs0LGOwQ",
"BAACAgEAAxkBAAIDRmnWqNvIk0GV0051QxjuXQjTDVLIAAJBCAAC9KC4RiJEk_m4MDL3OwQ"
]

PLANOS = {
    "leve": 5.00,
    "pesado": 8.99,
    "pesadissimo": 12.99,
    "completo": 15.99
}

def criar_pagamento(user_id, plano, extra=0):
    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
        json={
            "items": [{
                "title": plano,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": PLANOS[plano] + extra
            }],
            "external_reference": f"{user_id}|{plano}"
        }
    )
    return r.json().get("init_point")

# =============================
# REMARKETING
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    plano = usuarios.get(user_id, {}).get("clicou")
    if not plano:
        return

    link = criar_pagamento(user_id, plano)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text": f"👀 ei...\n\nvocê quase liberou o {plano} 😈\n\n👉 {link}"
        }
    )

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    registrar(user_id)

    keyboard = [[InlineKeyboardButton("😈 Entrar agora", callback_data="vip")]]

    await update.message.reply_text(
        "👀 achei que você não ia clicar...\n\nmas já que veio...\n👇",
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
            [InlineKeyboardButton("😈 Só olhar...", callback_data="leve")],
            [InlineKeyboardButton("🔥 Quero mais", callback_data="pesado")],
            [InlineKeyboardButton("👑 Sem limite", callback_data="pesadissimo")],
            [InlineKeyboardButton("💎 Tudo liberado", callback_data="completo")]
        ]

        await query.message.reply_text(
            "😏 até onde você aguenta?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        usuarios[user_id]["clicou"] = query.data

        asyncio.create_task(remarketing(user_id))

        await query.message.reply_text("👀 segura...")

        await asyncio.sleep(2)

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      json={"chat_id": user_id, "photo": FOTOS_LEVE[0]})

        link = criar_pagamento(user_id, query.data)

        keyboard = [[InlineKeyboardButton("😈 desbloquear", url=link)]]

        await query.message.reply_text(
            "😳 quer ver o resto?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# ENTREGA + UPSELL
# =============================

def enviar_leve(chat_id):
    for f in FOTOS_LEVE:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={"chat_id": chat_id, "photo": f})
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesado", 3.99)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "😳 isso foi leve...\n\nvocê não aguentaria o resto 😈",
              "reply_markup": {"inline_keyboard": [[{"text": "🔥 subir nível (+3,99)", "url": link}]]}})

def enviar_pesado(chat_id):
    enviar_leve(chat_id)

    for f in FOTOS_PESADO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", json={"chat_id": chat_id, "photo": f})
        time.sleep(1)

    for v in VIDEOS_PESADO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={"chat_id": chat_id, "video": v})
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesadissimo", 3.99)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "🔥 agora ficou sério...",
              "reply_markup": {"inline_keyboard": [[{"text": "👑 liberar máximo (+3,99)", "url": link}]]}})

def enviar_pesadissimo(chat_id):
    enviar_pesado(chat_id)

    for v in VIDEOS_PESADISSIMO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={"chat_id": chat_id, "video": v})
        time.sleep(1)

    link = criar_pagamento(chat_id, "completo", 3.99)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id,
              "text": "👑 agora você chegou perto...",
              "reply_markup": {"inline_keyboard": [[{"text": "💎 liberar tudo (+3,99)", "url": link}]]}})

def enviar_completo(chat_id):
    enviar_pesadissimo(chat_id)

    for v in VIDEOS_COMPLETO:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", json={"chat_id": chat_id, "video": v})
        time.sleep(1)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "💎 acesso total liberado 😈"})

# =============================
# LIBERAR (ADMIN)
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
# RUN
# =============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
