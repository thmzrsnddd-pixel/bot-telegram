# (CÓDIGO ORIGINAL MANTIDO + MELHORIAS)

# =============================
# NOVOS SISTEMAS
# =============================

import random

# =============================
# PROVA SOCIAL FAKE
# =============================

nomes_fake = ["Lucas", "Marcos", "Ana", "Pedro", "Julia", "Rafael"]

def prova_social():
    nome = random.choice(nomes_fake)
    return f"🔥 {nome} acabou de entrar no VIP agora"

# =============================
# ESCASSEZ FAKE
# =============================

def escassez():
    vagas = random.randint(3, 9)
    return f"⚠️ restam apenas {vagas} vagas hoje"

# =============================
# REMARKETING DUPLO
# =============================

async def remarketing(user_id):
    await asyncio.sleep(120)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text":
            f"{prova_social()}\n\n"
            "😈 você sumiu...\n\n"
            "🔥 24h VIP por R$5\n"
            f"{escassez()}\n\n"
            f"👉 {link}"
        }
    )

    # SEGUNDO ATAQUE (5 min depois)
    await asyncio.sleep(300)

    if tem_acesso(user_id):
        return

    link = criar_pagamento(user_id, "isca")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": user_id,
            "text":
            "⏳ última chance...\n\n"
            "vou tirar essa oferta em instantes\n\n"
            f"{escassez()}\n\n"
            f"👉 {link}"
        }
    )

# =============================
# BOTÕES MELHORADOS
# =============================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "vip":

        salvar_interesse(user_id)
        asyncio.create_task(remarketing(user_id))

        keyboard = [
            [InlineKeyboardButton("🔥 TESTE 24H R$5", callback_data="isca")],
            [InlineKeyboardButton("👑 VIP 15 DIAS R$22,99", callback_data="15d")],
            [InlineKeyboardButton("🔥 VIP 7 DIAS R$14,99", callback_data="7d")],
            [InlineKeyboardButton("💰 VIP 1 DIA R$7", callback_data="1d")],
            [InlineKeyboardButton("📦 ACESSO COMPLETO R$10,99", callback_data="pack")]
        ]

        await query.message.reply_video(
            video=VIDEO_VIP,
            caption=
            f"{prova_social()}\n\n"
            "😈 você não deveria estar vendo isso...\n\n"
            "💦 conteúdo proibido\n"
            "🔥 atualizado sempre\n\n"
            f"{escassez()}\n\n"
            "👇 entra enquanto dá:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PLANOS:

        await query.message.reply_text("⏳ liberando acesso...")

        time.sleep(1.5)

        link = criar_pagamento(user_id, query.data)

        await query.message.reply_text(
            f"{prova_social()}\n\n"
            f"🔥 {PLANOS[query.data]['nome']}\n\n"
            f"{escassez()}\n\n"
            f"👉 {link}"
        )

# =============================
# UPSELL AUTOMÁTICO
# =============================

def enviar_vip(chat_id, plano):
    chat_id = int(chat_id)

    remover_interesse(chat_id)
    liberar_acesso(chat_id, PLANOS[plano]["dias"])

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": "😈 acesso liberado... aproveita 😏"}
    )

    # UPSELL (APÓS COMPRA)
    if plano == "isca" or plano == "1d":
        link = criar_pagamento(chat_id, "15d")

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text":
                "😳 você gostou né...\n\n"
                "🔥 libera tudo por 15 dias com desconto\n\n"
                f"{escassez()}\n\n"
                f"👉 {link}"
            }
        )
