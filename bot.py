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
# HANDLERS
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia 👀", callback_data="previa")],
        [InlineKeyboardButton("🔒 Conteúdo VIP 🔒", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)]
    ]

    await update.message.reply_text(
        "😈 Oi amor...\n\nQuer ver tudo? 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "previa":
        await query.message.reply_text("👀 Só uma prévia...\nO resto é VIP 😈")

    elif query.data == "vip":
        if user_id in usuarios_vip:
            await query.message.reply_text("🔥 VIP liberado 😈")
        else:
            await query.message.reply_text("🔒 Conteúdo VIP bloqueado!\n\n💸 Libera agora 😈")

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
# SET WEBHOOK NA SUBIDA (SEM before_first_request)
# =============================

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    try:
        r = requests.get(url, params={"url": webhook_url})
        print("Webhook setado:", r.text)
    except Exception as e:
        print("Erro ao setar webhook:", e)


# roda automaticamente quando o gunicorn sobe
set_webhook()
