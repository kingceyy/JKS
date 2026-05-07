
from aiohttp import web
from .route import routes
from asyncio import sleep
from datetime import datetime
from database.users_chats_db import db
from info import LOG_CHANNEL, MINI_APP_URL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def check_expired_premium(client):
    """
    Tâche de fond qui tourne en boucle toutes les 60s.
    1. Expire les plans premium → notifie l'utilisateur avec bouton Mini App.
    2. Expire les sessions gratuites → notifie l'utilisateur avec bouton Mini App.
    """
    while 1:
        now = datetime.utcnow()

        # ── 1. Plans premium expirés ──────────────────────────────────────────
        data = await db.get_expired(now)
        for user_doc in data:
            user_id = user_doc["id"]
            await db.remove_premium_access(user_id)
            try:
                user = await client.get_users(user_id)
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"<b>⏰ {user.mention}, votre plan Premium a expiré.</b>\n\n"
                        "Votre accès illimité est terminé.\n\n"
                        "• Regardez une publicité pour <b>1 heure d'accès gratuit</b>\n"
                        "• Ou renouvelez votre plan Premium pour un accès illimité\n\n"
                        "Appuyez sur le bouton ci-dessous pour ouvrir la Mini App :"
                    ),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            "🎬 Ouvrir JKS Mini App",
                            web_app={"url": MINI_APP_URL}
                        )
                    ]]),
                    parse_mode="html",
                )
                await client.send_message(
                    LOG_CHANNEL,
                    text=(
                        f"<b>#Premium_Expire</b>\n\n"
                        f"Utilisateur : {user.mention}\n"
                        f"ID : <code>{user_id}</code>"
                    ),
                    parse_mode="html",
                )
            except Exception as e:
                print(f"[check_expired_premium] premium notify error for {user_id}: {e}")
            await sleep(0.5)

        # ── 2. Sessions gratuites expirées ────────────────────────────────────
        try:
            expired_sessions = await db.col.find({
                "session_expiry": {"$lt": now, "$ne": None}
            }).to_list(length=200)

            for user_doc in expired_sessions:
                user_id = user_doc.get("id")
                if not user_id:
                    continue
                # Efface la session expirée en base
                await db.col.update_one(
                    {"id": user_id},
                    {"$set": {"session_expiry": None}}
                )
                try:
                    user = await client.get_users(user_id)
                    await client.send_message(
                        chat_id=user_id,
                        text=(
                            f"<b>⌛ {user.mention}, votre session gratuite a expiré.</b>\n\n"
                            "Vous n'avez plus accès aux fichiers du bot.\n\n"
                            "Regardez une publicité pour obtenir <b>1 heure d'accès gratuit</b>.\n"
                            "Ou souscrivez à un plan Premium pour un accès illimité.\n\n"
                            "Appuyez sur le bouton ci-dessous :"
                        ),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                "📺 Regarder une pub — Accès 1h",
                                web_app={"url": MINI_APP_URL}
                            )
                        ]]),
                        parse_mode="html",
                    )
                except Exception as e:
                    print(f"[check_expired_premium] session notify error for {user_id}: {e}")
                await sleep(0.5)
        except Exception as e:
            print(f"[check_expired_premium] session query error: {e}")

        await sleep(60)  # Vérification toutes les 60 secondes
