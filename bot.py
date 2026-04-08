from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import requests
import time
import json
import os
import threading
import asyncio

# =============================
# CONFIG
# =============================

TOKEN = "8705199333:AAGURCHtpVxni0b25b_QgsjQAQlxMjPuby0"
PUBLIC_URL = "https://bot-telegram-jdwg.onrender.com"
MP_ACCESS_TOKEN = "APP_USR-1181155738357521-040514-9f16dd5519b7511a3d63a61f64300b1f-2931893365"

ADMIN_ID = 8584498503

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

DB_FILE = "usuarios.json"
INTERESSE_FILE = "interesse.json"

# =============================
# MIDIA
# =============================

FOTO_START = "AgACAgEAAxkBAAIBW2nVAAHA4MmTOu-BxgLp5jg8Ki_BSwACGAxrG6ZgqUZa618MB7ra7wEAAwIAA3kAAzsE"
VIDEO_VIP = "BAACAgEAAyEFAATanvxOAAMUadUHHCYG4cpssnNLzoS_9tzrQAgAAvoHAAKmYKlGY1cOvM0Wqzw7BA"

MIDIAS_VIP = list({
    ("foto", "AgACAgEAAxkBAAIBXGnVAAHAb5B3BdUxiosov-1dgCmJKwACFwxrG6ZgqUaMyF1kSngZSgEAAwIAA3kAAzsE"),
    ("foto", "AgACAgEAAxkBAAIBXWnVAAHAbVGKwRoQSJjZ3BNnHh7NqQACGQxrG6ZgqUbCJc8OBDvJYwEAAwIAA3kAAzsE"),
    ("foto", "AgACAgEAAxkBAAIBXmnVAAHAtv9eH4pPF3wWgNnAbEAOHwACGgxrG6ZgqUbO0Js_MMVsjgEAAwIAA3kAAzsE"),
    ("foto", "AgACAgEAAxkBAAIBX2nVAAHAXPd6uwjw7pDhicxr3YTsUwACGwxrG6ZgqUaPWpNpw3MxMAEAAwIAA3kAAzsE"),
    ("foto", "AgACAgEAAxkBAAIBYGnVAAHAbnPgUhD1y1LTKG71eWe53AACHAxrG6ZgqUZMfSFoc5X4AQEAAwIAA3kAAzsE"),
    ("video", "BAACAgEAAxkBAAIBYWnVAAHA7W2a3yrYP0gvzOmZO10dMQAC6wcAAqZgqUa6m46Dvr58qjsE"),
    ("video", "BAACAgEAAxkBAAIBYmnVAAHAeHwHLWHdbsLbnNUvLIaoVgAC8QcAAqZgqUbtoS5YWN_WPjsE"),
    ("video", "BAACAgEAAxkBAAIBY2nVAAHAYPdq3KsobU8gX9sl2dp2GwAC7AcAAqZgqUYDC8pyBIDwsDsE"),
}).copy()

MIDIAS_VIP = [{"tipo": t, "id": i} for t, i in MIDIAS_VIP]

# =============================
# PLANOS
# =============================

PLANOS = {
    "isca": {"dias": 1, "preco": 4.50, "nome": "🔥 OFERTA SECRETA 24H"},
    "teste": {"dias": 1, "preco": 6.99, "nome": "🔥 TESTE VIP 24H"},
    "7d": {"dias": 7, "preco": 14.99, "nome": "🔥 7 DIAS VIP"},
    "15d": {"dias": 15, "preco": 22.99, "nome": "👑 15 DIAS VIP"},
    "pack": {"dias": 999, "preco": 10.99, "nome": "📦 COMPLETO"}
}

# =============================
# BANCO
# =============================

def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def salvar_usuarios(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def liberar_acesso(user_id, dias):
    usuarios = carregar_usuarios()

    if dias == 999:
        usuarios[str(user_id)] = 9999999999
    else:
        usuarios[str(user_id)] = int(time.time()) + dias * 86400

    salvar_usuarios(usuarios)

# =============================
# PAGAMENTO
# =============================

def criar_pagamento(user_id, plano):
    plano_info = PLANOS[plano]

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "items": [{
                "title": plano_info["nome"],
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(plano_info["preco"])
            }],
            "external_reference": f"{user_id}|{plano}"
        }
    )

    return r.json().get("init_point", "erro")

# =============================
# ENTREGA
# =============================

def enviar_vip(chat_id, plano):
    liberar_acesso(chat_id, PLANOS[plano]["dias"])

    enviados = set()

    for midia in MIDIAS_VIP:
        if midia["id"] in enviados:
            continue

        enviados.add(midia["id"])

        time.sleep(1.2)

        if midia["tipo"] == "foto":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": midia["id"], "protect_content": True}
            )
        else:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                json={"chat_id": chat_id, "video": midia["id"], "protect_content": True}
            )
