# =============================
# ENTREGA + UPSELL (CORRIGIDO)
# =============================

def enviar_leve(chat_id):
    for f in FOTOS_LEVE:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": f}
        )
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesado", 3.99)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "😳 isso foi leve...\n\nvocê não aguentaria o resto 😈",
            "reply_markup": {
                "inline_keyboard": [[{"text": "🔥 subir nível (+3,99)", "url": link}]]
            }
        }
    )


def enviar_pesado(chat_id):
    for f in FOTOS_PESADO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": f}
        )
        time.sleep(1)

    for v in VIDEOS_PESADO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": v}
        )
        time.sleep(1)

    link = criar_pagamento(chat_id, "pesadissimo", 3.99)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "🔥 agora ficou sério...\n\nmas ainda não é tudo 😈",
            "reply_markup": {
                "inline_keyboard": [[{"text": "👑 liberar máximo (+3,99)", "url": link}]]
            }
        }
    )


def enviar_pesadissimo(chat_id):
    for v in VIDEOS_PESADISSIMO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": v}
        )
        time.sleep(1)

    link = criar_pagamento(chat_id, "completo", 3.99)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "👑 agora você chegou perto...\n\nquer TUDO mesmo? 😈",
            "reply_markup": {
                "inline_keyboard": [[{"text": "💎 liberar tudo (+3,99)", "url": link}]]
            }
        }
    )


def enviar_completo(chat_id):
    # envia TUDO (sem upsell)
    for f in FOTOS_LEVE:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": f}
        )
        time.sleep(1)

    for f in FOTOS_PESADO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": f}
        )
        time.sleep(1)

    for v in VIDEOS_PESADO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": v}
        )
        time.sleep(1)

    for v in VIDEOS_PESADISSIMO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": v}
        )
        time.sleep(1)

    for v in VIDEOS_COMPLETO:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendVideo",
            json={"chat_id": chat_id, "video": v}
        )
        time.sleep(1)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "💎 acesso total liberado 😈\n\nagora você viu tudo..."
        }
    )
