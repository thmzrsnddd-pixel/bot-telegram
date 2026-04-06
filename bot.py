from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import threading
import requests
import asyncio

# 🔑 CONFIG
TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"
LINK_PAGAMENTO = "https://mpago.la/2KwTbi7"

bot = Bot(token=TOKEN)

# 📦 Controle
usuarios_esperando = {}
usuarios_compraram = set()

# 🤖 BOT
app_bot = ApplicationBuilder().token(TOKEN).build()

# 🌐 WEBHOOK
app = Flask(__name__)

# 🔓 LIBERAR ACESSO
async def liberar_acesso(user_id):
    await bot.send_message(
        chat_id=user_id,
        text="🔓 PAGAMENTO CONFIRMADO!\n\nAproveite 😈🔥"
    )

    await bot.send_video(
        chat_id=user_id,
        video=open(r"C:\Users\123\Desktop\IMG_1012.mp4", "rb")
    )

# ▶️ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Ver Prévia", callback_data="previa")],
        [InlineKeyboardButton("💎 Conteúdo VIP", callback_data="vip")],
        [InlineKeyboardButton("💰 Comprar Acesso", callback_data="comprar")],
        [InlineKeyboardButton("❓ Dúvidas", callback_data="duvidas")]
    ]

    await update.message.reply_photo(
        photo=open(r"C:\Users\123\Desktop\foto.jpg.jpg", "rb"),
        caption="Escolha uma opção 😈🔥",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BOTÕES
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 🔥 Prévia
    if query.data == "previa":
        await query.message.reply_video(
            video=open(r"C:\Users\123\Desktop\IMG_1012.mp4", "rb"),
            caption="🔥 Só um gostinho...\n\nO resto é VIP 😈"
        )

    # 💎 VIP
    elif query.data == "vip":
        keyboard = [
            [InlineKeyboardButton("💰 Comprar Acesso", callback_data="comprar")]
        ]

        await query.message.reply_text(
            "🔒 Conteúdo VIP BLOQUEADO\n\n"
            "🔥 Vídeos exclusivos\n"
            "🔥 Atualizações frequentes\n"
            "🔥 Conteúdo sem censura\n\n"
            "💰 Libere agora por R$10",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 💰 COMPRAR
    elif query.data == "comprar":
        user_id = query.from_user.id

        # salva quem está pagando
        usuarios_esperando[user_id] = True

        await query.message.reply_text(
            f"💰 PAGUE AQUI:\n{LINK_PAGAMENTO}\n\n"
            "⚠️ Após pagar, aguarde liberação automática 😈"
        )

    # ❓ DÚVIDAS
    elif query.data == "duvidas":
        await query.message.reply_text("Me chama 😉")

# 🌐 WEBHOOK MERCADO PAGO
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📩 Webhook recebido:", data)

    try:
        if "data" in data and "id" in data["data"]:
            payment_id = data["data"]["id"]

            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {
                "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
            }

            response = requests.get(url, headers=headers)
            pagamento = response.json()

            print("💰 Status pagamento:", pagamento.get("status"))

            if pagamento.get("status") == "approved":
                for user_id in list(usuarios_esperando.keys()):
                    usuarios_esperando.pop(user_id)
                    usuarios_compraram.add(user_id)

                    asyncio.run(liberar_acesso(user_id))
                    break

    except Exception as e:
        print("Erro no webhook:", e)

    return "ok", 200

# 🚀 INICIAR BOT (SEM POLLING)
def iniciar_bot():
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot pronto (modo webhook)")

# 🚀 INICIAR WEBHOOK
def iniciar_webhook():
    print("🌐 Webhook rodando...")
    app.run(port=8000)

# 🔥 START
threading.Thread(target=iniciar_bot).start()
threading.Thread(target=iniciar_webhook).start()