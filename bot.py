from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os

# =============================
# CONFIG
# =============================

TOKEN = "SEU_TOKEN_AQUI"  # TROCA ISSO DEPOIS
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
LINK_PAGAMENTO = "https://mpago.la/2KwTbi7"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios_vip = set()

# caminho base (ESSENCIAL PRO RENDER)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia 👀", callback_data="previa")],
        [InlineKeyboardButton("🔒 Conteúdo VIP 🔒", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)]
    ]

    try:
        caminho_foto = os.path.join(BASE_DIR, "foto1.jpg")

        with open(caminho_foto, "rb") as foto:
            await update.message.reply_photo(
                photo=foto,
                caption="😈 Oi amor...\n\nQuer ver tudo? 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        print("ERRO FOTO START:", e)
        await update.message.reply_text("Erro ao carregar mídia 😢")

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "previa":
        try:
            caminho_video = os.path.join(BASE_DIR, "video1.mp4")

            with open(caminho_video, "rb") as video:
                await query.message.reply_video(
                    video=video,
                    caption="👀 Só uma prévia...\nO resto é VIP 😈"
                )

        except Exception as e:
            print("ERRO VIDEO:", e)
            await query.message.reply_text("Erro ao carregar vídeo 😢")

    elif query.data == "vip":
        try:
            caminho_foto2 = os.path.join(BASE_DIR, "foto2.jpg")

            with open(caminho_foto2, "rb") as foto:
                if user_id in usuarios_vip:
                    await query.message.reply_photo(
                        photo=foto,
                        caption="🔥 VIP liberado 😈"
                    )
                else:
                    await query.message.reply_photo(
                        photo=foto,
                        caption="🔒 Conteúdo VIP bloqueado!\n\n💸 Libera agora 😈"
                    )

        except Exception as e:
            print("ERRO FOTO VIP:", e)
            await query.message.reply_text("Erro ao carregar conteúdo 😢")

# =============================
# HANDLERS
# =============================

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(botoes))

# =============================
# WEBHOOK
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
# SET WEBHOOK
# =============================

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    try:
        r = requests.get(url, params={"url": webhook_url})
        print("Webhook setado:", r.text)
    except Exception as e:
        print("Erro webhook:", e)

set_webhook()
