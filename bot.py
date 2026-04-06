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
# START (BOAS-VINDAS + FOTO)
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("👀 Ver prévia 👀", callback_data="previa")],
        [InlineKeyboardButton("🔒 Conteúdo VIP 🔒", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)]
    ]

    await update.message.reply_photo(
        photo=open("foto1.jpg", "rb"),
        caption="😈 Oi amor...\n\nQuer ver tudo? 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # 👀 PRÉVIA (VÍDEO)
    if query.data == "previa":
        await query.message.reply_video(
            video=open("video1.mp4", "rb"),
            caption="👀 Só uma prévia...\nO resto é VIP 😈"
        )

    # 🔒 VIP (FOTO + BLOQUEIO)
    elif query.data == "vip":
        if user_id in usuarios_vip:
            await query.message.reply_photo(
                photo=open("foto2.jpg", "rb"),
                caption="🔥 VIP liberado 😈"
            )
        else:
            await query.message.reply_photo(
                photo=open("foto2.jpg", "rb"),
                caption="🔒 Conteúdo VIP bloqueado!\n\n💸 Libera agora e acessa tudo 😈"
            )

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
    return "OK", 200


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, bot_app.bot)
    asyncio.run(bot_app.process_update(update))

    return "ok", 200

# =============================
# INICIAR BOT
# =============================

async def iniciar_bot():
    print("🚀 Bot iniciando...")

    await bot_app.initialize()
    await bot_app.start()

    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{PUBLIC_URL}/webhook/{TOKEN}"

    r = requests.get(url, params={"url": webhook_url})
    print("Webhook:", r.text)

# =============================
# START APP
# =============================

if __name__ == "__main__":
    import threading

    threading.Thread(target=lambda: asyncio.run(iniciar_bot())).start()

    app.run(host="0.0.0.0", port=10000)
