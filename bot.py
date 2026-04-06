from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os
import json

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
LINK_PAGAMENTO = "https://mpago.la/2KwTbi7"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIP_FILE = os.path.join(BASE_DIR, "vip.json")

# =============================
# BANCO DE VIP (arquivo)
# =============================

def carregar_vip():
    if not os.path.exists(VIP_FILE):
        return set()
    with open(VIP_FILE, "r") as f:
        return set(json.load(f))

def salvar_vip(vips):
    with open(VIP_FILE, "w") as f:
        json.dump(list(vips), f)

usuarios_vip = carregar_vip()

# =============================
# HANDLERS
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia 👀", callback_data="previa")],
        [InlineKeyboardButton("🔒 Conteúdo VIP 🔒", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)]
    ]

    try:
        with open(os.path.join(BASE_DIR, "foto1.jpg"), "rb") as foto:
            await update.message.reply_photo(
                photo=foto,
                caption="😈 Oi amor...\n\nConteúdo exclusivo te esperando 👇🔥",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        print("ERRO FOTO:", e)
        await update.message.reply_text("Erro ao carregar imagem")

# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # ================= PREVIA =================
    if query.data == "previa":
        try:
            with open(os.path.join(BASE_DIR, "foto2.jpg"), "rb") as foto:
                await query.message.reply_photo(
                    photo=foto,
                    caption="👀 Só uma prévia...\nO resto é VIP 😈"
                )
        except Exception as e:
            print("ERRO PREVIA:", e)

    # ================= VIP =================
    elif query.data == "vip":
        try:
            keyboard = [
                [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)]
            ]

            if user_id in usuarios_vip:
                with open(os.path.join(BASE_DIR, "video1.mp4"), "rb") as video:
                    await query.message.reply_video(
                        video=video,
                        caption="🔥 VIP liberado 😈",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            else:
                await query.message.reply_text(
                    "🔒 Conteúdo VIP bloqueado!\n\n💸 Libere agora 😈",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        except Exception as e:
            print("ERRO VIP:", e)

# =============================
# REGISTRO HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# WEBHOOK TELEGRAM
# =============================

@app.route("/", methods=["GET"])
def home():
    return "BOT ONLINE", 200


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)

    async def run():
        await bot_app.initialize()
        await bot_app.process_update(update)

    asyncio.run(run())

    return "ok", 200

# =============================
# WEBHOOK MERCADO PAGO (AUTOMÁTICO)
# =============================

@app.route("/mp", methods=["POST"])
def mercado_pago():
    global usuarios_vip

    data = request.get_json()
    print("MP DATA:", data)

    try:
        if data.get("type") == "payment":
            user_id = data.get("data", {}).get("id")

            # 🔥 AQUI você pode melhorar depois com validação real
            # por enquanto libera direto

            if user_id:
                usuarios_vip.add(user_id)
                salvar_vip(usuarios_vip)

                # envia mensagem no telegram
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, json={
                    "chat_id": user_id,
                    "text": "🔥 Pagamento aprovado! VIP liberado 😈"
                })

    except Exception as e:
        print("ERRO MP:", e)

    return "ok", 200

# =============================
# SET WEBHOOK TELEGRAM
# =============================

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    try:
        r = requests.get(url, params={"url": webhook_url})
        print("Webhook Telegram:", r.text)
    except Exception as e:
        print("Erro webhook:", e)

set_webhook()
