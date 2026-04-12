from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
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
# ARQUIVOS
# =============================

def carregar(nome):
    if not os.path.exists(nome):
        with open(nome, "w") as f:
            json.dump([], f)
    with open(nome, "r") as f:
        return json.load(f)

def salvar(nome, data):
    with open(nome, "w") as f:
        json.dump(data, f)

# =============================
# BANCO SIMPLES
# =============================

ARQ_PAG = "pagamentos.json"
ARQ_VIP = "vip.json"

# =============================
# MIDIAS
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
# LIBERAR CONTEÚDO
# =============================

def liberar_conteudo(user_id, plano):
    vip = carregar(ARQ_VIP)

    if user_id not in vip:
        vip.append(user_id)
        salvar(ARQ_VIP, vip)

    if plano == "leve":
        for f in FOTOS:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          json={"chat_id": user_id, "photo": f,
                                "caption": "🔒 conteúdo protegido"})
            time.sleep(1)

        # 🔥 UPSELL
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": user_id,
                "text": "quer ver mais pesado? 😈\n\nlibero por só R$4,99",
            })

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
# WEBHOOK MP
# =============================

@app.route("/mp", methods=["POST"])
def mp():
    data = request.get_json()

    if data.get("type") == "payment":
        pid = str(data["data"]["id"])
        pagos = carregar(ARQ_PAG)

        if pid in pagos:
            return "ok", 200

        pagos.append(pid)
        salvar(ARQ_PAG, pagos)

        pagamento = requests.get(
            f"https://api.mercadopago.com/v1/payments/{pid}",
            headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        ).json()

        if pagamento.get("status") == "approved":
            user_id, plano = pagamento["external_reference"].split("|")
            threading.Thread(target=liberar_conteudo,
                             args=(int(user_id), plano)).start()

    return "ok", 200

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("😈 entrar", callback_data="vip")]]

    await update.message.reply_text("entra 😈", reply_markup=InlineKeyboardMarkup(keyboard))

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("😈 LEVE", callback_data="leve")],
        [InlineKeyboardButton("🔥 PESADO", callback_data="pesado")],
        [InlineKeyboardButton("💀 PESADÍSSIMO", callback_data="pesadissimo")],
    ]

    await query.message.reply_text("escolhe 😈", reply_markup=InlineKeyboardMarkup(keyboard))

# =============================
# LIBERAR ADMIN
# =============================

async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    liberar_conteudo(ADMIN_ID, "pesadissimo")
    await update.message.reply_text("ok")

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    loop.run_until_complete(bot_app.process_update(update))
    return "ok"

# =============================
# ROOT
# =============================

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
