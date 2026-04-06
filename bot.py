from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import asyncio
import requests
import os

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
LINK_PAGAMENTO = "https://mpago.la/2KwTbi7"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

usuarios_vip = set()

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

    with open(os.path.join(BASE_DIR, "foto1.jpg"), "rb") as foto:
        await update.message.reply_photo(
            photo=foto,
            caption="😈 Oi amor... sua garotinha está aqui 🔥\n\n🔞 Conteúdo exclusivo 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # 👀 PRÉVIA = FOTO
    if query.data == "previa":
        with open(os.path.join(BASE_DIR, "foto2.jpg"), "rb") as foto:
            await query.message.reply_photo(
                photo=foto,
                caption="👀 Só uma prévia...\nO resto é VIP 😈"
            )

    # 🔒 VIP
    elif query.data == "vip":

        # se já é VIP → manda vídeo
        if user_id in usuarios_vip:
            with open(os.path.join(BASE_DIR, "video1.mp4"), "rb") as video:
                await query.message.reply_video(
                    video=video,
                    caption="🔥 VIP liberado 😈"
                )

        # se NÃO é VIP → mostra botões
        else:
            keyboard = [
                [InlineKeyboardButton("💰 Comprar acesso", url=LINK_PAGAMENTO)],
                [InlineKeyboardButton("✅ Já paguei (teste)", callback_data="liberar_vip")]
            ]

            await query.message.reply_text(
                "🔒 Conteúdo VIP bloqueado!\n\nLibere agora 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # 🔓 LIBERAR VIP (TESTE)
    elif query.data == "liberar_vip":
        usuarios_vip.add(user_id)

        await query.message.reply_text("✅ VIP liberado! Clique novamente em VIP 😈")

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
        print("Webhook:", r.text)
    except Exception as e:
        print("Erro webhook:", e)

set_webhook()
