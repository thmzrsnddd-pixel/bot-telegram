from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import asyncio
import requests

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# =============================
# MIDIAS
# =============================

FOTO_START = "AgACAgEAAxkBAAIBW2nVAAHA4MmTOu-BxgLp5jg8Ki_BSwACGAxrG6ZgqUZa618MB7ra7wEAAwIAA3kAAzsE"

VIDEO_VIP = "BAACAgEAAyEFAATanvxOAAMUadUHHCYG4cpssnNLzoS_9tzrQAgAAvoHAAKmYKlGY1cOvM0Wqzw7BA"

MIDIAS_VIP = [
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXGnVAAHAb5B3BdUxiosov-1dgCmJKwACFwxrG6ZgqUaMyF1kSngZSgEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXWnVAAHAbVGKwRoQSJjZ3BNnHh7NqQACGQxrG6ZgqUbCJc8OBDvJYwEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBXmnVAAHAtv9eH4pPF3wWgNnAbEAOHwACGgxrG6ZgqUbO0Js_MMVsjgEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBX2nVAAHAXPd6uwjw7pDhicxr3YTsUwACGwxrG6ZgqUaPWpNpw3MxMAEAAwIAA3kAAzsE"},
    {"tipo": "foto", "id": "AgACAgEAAxkBAAIBYGnVAAHAbnPgUhD1y1LTKG71eWe53AACHAxrG6ZgqUZMfSFoc5X4AQEAAwIAA3kAAzsE"},

    {"tipo": "video", "id": "BAACAgEAAxkBAAIBYmnVAAHAeHwHLWHdbsLbnNUvLIaoVgAC8QcAAqZgqUbtoS5YWN_WPjsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBY2nVAAHAYPdq3KsobU8gX9sl2dp2GwAC7AcAAqZgqUYDC8pyBIDwsDsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBZGnVAAHAO7O3Vtsh6t7BzFAgCgkX7QAC9gcAAqZgqUaNNQWAeadz-DsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBfGnVBDC9xZw0FtseNIzz_FmR4XeEAALzBwACpmCpRocrceFUB73EOwQ"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBfWnVBDAgot9YitzGPmm3lA9t6kSIAALvBwACpmCpRtExmf_B8lfTOwQ"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBfmnVBDBjaiN9Vl35M3JCKJaaXvVqAAL1BwACpmCpRjv8Dep8J5t7OwQ"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBf2nVBDD0eCe5q-ubUy_otnlgyi3sAAL0BwACpmCpRiVTPvWB3cjvOwQ"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBZWnVAAHL7IUtQjRlXHLqxMctEnOhrAAC8AcAAqZgqUYSiKkeHt5nZDsE"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBgWnVBDCfWfEuMqrOFrb3nojMRpu9AALtBwACpmCpRq4zyCG12sCjOwQ"},
    {"tipo": "video", "id": "BAACAgEAAxkBAAIBgmnVBDAsry3P8cvIVvq_3KFeZ_k4AALuBwACpmCpRr2Z6PiI2y82OwQ"},
]

# =============================
# START
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("Ver previa", callback_data="previa")],
        [InlineKeyboardButton("VIP", callback_data="vip")]
    ]

    await update.message.reply_photo(
        photo=FOTO_START,
        caption=(
            "Oi... eu tava te esperando\n\n"
            "nao costumo mostrar isso pra qualquer um...\n\n"
            "mas se voce quiser ver mais..."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =============================
# BOTÕES
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "previa":
        await query.message.reply_text(
            "isso aqui e so uma previa..."
        )

    elif query.data == "vip":

        keyboard = [
            [InlineKeyboardButton("1 DIA", callback_data="1d")],
            [InlineKeyboardButton("7 DIAS", callback_data="7d")],
            [InlineKeyboardButton("15 DIAS", callback_data="15d")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption="isso aqui e so uma parte...",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =============================
# ENVIAR MIDIAS VIP
# =============================

async def enviar_midias(chat_id):
    for midia in MIDIAS_VIP:
        try:
            if midia["tipo"] == "foto":
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                    json={"chat_id": chat_id, "photo": midia["id"]}
                )

            elif midia["tipo"] == "video":
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                    json={"chat_id": chat_id, "video": midia["id"]}
                )

        except Exception as e:
            print("ERRO MIDIA:", e)

# =============================
# WEBHOOK
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
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
