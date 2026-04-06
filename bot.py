from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
LINK_PAGAMENTO = "https://mpago.la/2KwTbi7"

app = Flask(__name__)

bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios_vip = set()

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
        with open("foto1.jpg", "rb") as foto:
            await update.message.reply_photo(
                photo=foto,
                caption="😈 Oi amor...\n\nQuer ver tudo? 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        await update.message.reply_text("Erro ao carregar mídia.")

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "previa":
        try:
            with open("video1.mp4", "rb") as video:
                await query.message.reply_video(
                    video=video,
                    caption="👀 Só uma prévia...\nO resto é VIP 😈"
                )
        except:
            await query.message.reply_text("Erro ao enviar vídeo.")

    elif query.data == "vip":
        try:
            with open("foto2.jpg", "rb") as foto:
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
        except:
            await query.message.reply_text("Erro ao carregar conteúdo.")

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
    try:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)

        asyncio.run(bot_app.process_update(update))

        return "ok", 200

    except Exception as e:
        print("ERRO:", e)
        return "error", 500

# =============================
# INICIALIZAÇÃO
# =============================

async def setup():
    await bot_app.initialize()
    await bot_app.start()

    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": webhook_url}
    )

    print("Webhook configurado!")

# roda ao iniciar (GUNICORN)
@app.before_first_request
def iniciar():
    asyncio.run(setup())
