# plugins/web_app_handler.py

import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from database.jks_db import grant_free_session, grant_premium_plan, format_expiry
from info import LOG_CHANNEL

logger = logging.getLogger(__name__)


# ── Filtre web_app_data ────────────────────────────────────────────────────────

web_app_data_filter = filters.create(
    lambda _, __, message: message.web_app_data is not None,
    name="WebAppDataFilter"
)


@Client.on_message(filters.private & web_app_data_filter)
async def handle_web_app_data(client: Client, message: Message):
    """
    Reçoit les données de la Mini App JKS via Telegram WebApp.sendData().
    Actions supportées :
      - ad_watched   : pub vue → session 1h gratuite
      - ton_payment  : paiement TON confirmé côté client → activation plan premium
    """
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    try:
        raw = message.web_app_data.data
        payload = json.loads(raw)
    except Exception as e:
        logger.error(f"[WebApp] Payload invalide reçu de {user_id} : {e}")
        await message.reply_text(
            "<b>Une erreur est survenue.</b>\n\n"
            "Veuillez réessayer depuis la Mini App.\n"
            "Si le problème persiste, contactez le support.",
            parse_mode="html"
        )
        return

    action = payload.get("action")

    # ── Action : pub vue → session 1h ─────────────────────────────────────────
    if action == "ad_watched":
        try:
            expiry = await grant_free_session(user_id)
            expiry_str = format_expiry(expiry)

            await message.reply_text(
                "<b>Session activée avec succès !</b>\n\n"
                "Vous avez maintenant accès à tous les fichiers pendant <b>1 heure</b>.\n\n"
                f"Expiration : <code>{expiry_str}</code>\n\n"
                "Retournez dans le groupe et effectuez vos recherches librement.",
                parse_mode="html"
            )

            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=(
                    "<b>#SESSION_GRATUITE</b>\n\n"
                    f"Utilisateur : {user_mention}\n"
                    f"ID : <code>{user_id}</code>\n"
                    f"Expiration : <code>{expiry_str}</code>\n"
                    f"Méthode : Pub regardée via Mini App"
                ),
                parse_mode="html"
            )

        except Exception as e:
            logger.error(f"[WebApp] Erreur grant_free_session pour {user_id} : {e}")
            await message.reply_text(
                "<b>Erreur lors de l'activation de votre session.</b>\n\n"
                "Veuillez contacter le support.",
                parse_mode="html"
            )

    # ── Action : paiement TON confirmé ────────────────────────────────────────
    elif action == "ton_payment":
        """
        La Mini App envoie cette action après que l'utilisateur a validé
        la transaction TON Connect côté client.

        Payload attendu :
          {
            "action": "ton_payment",
            "plan": "or",            # clé du plan
            "days": 60,              # durée en jours
            "tx_boc": "...",         # identifiant BOC de la transaction
            "amount_ton": "1.2345",  # montant TON (informatif)
            "amount_nano": "1234..."  # montant en nanotons (informatif)
          }

        SÉCURITÉ IMPORTANTE :
        Ce handler active le plan de façon optimiste (bonne UX) mais tu DOIS
        aussi implémenter une vérification on-chain côté bot via l'API TON Center
        (https://toncenter.com/api/v2/) pour confirmer que la transaction existe
        et que le montant est correct avant d'activer en production.
        """
        plan_key = payload.get("plan")
        days = payload.get("days")
        tx_boc = payload.get("tx_boc", "N/A")
        amount_ton = payload.get("amount_ton", "?")

        # Valide la clé de plan
        VALID_PLANS = {"bronze", "argent", "or", "platine", "diamant", "adamantide"}
        if plan_key not in VALID_PLANS:
            logger.warning(f"[WebApp/TON] Plan inconnu '{plan_key}' de {user_id}")
            await message.reply_text(
                "<b>Erreur : plan inconnu.</b>\nContactez le support.",
                parse_mode="html"
            )
            return

        try:
            # ── TODO production : vérification on-chain ────────────────────
            # Avant d'activer, vérifie que tx_boc correspond à une vraie
            # transaction vers TON_WALLET_ADDRESS avec le bon montant.
            # Exemple :
            #   verified = await verify_ton_transaction(tx_boc, expected_nano)
            #   if not verified: raise ValueError("Transaction non confirmée")
            # ─────────────────────────────────────────────────────────────────

            expiry = await grant_premium_plan(user_id, plan_key)
            expiry_str = format_expiry(expiry)

            from database.jks_db import PLAN_LABELS
            plan_label = PLAN_LABELS.get(plan_key, plan_key)

            await message.reply_text(
                f"<b>✅ Plan {plan_label} activé !</b>\n\n"
                f"Durée : <b>{days} jours</b>\n"
                f"Expiration : <code>{expiry_str}</code>\n\n"
                "Vous bénéficiez maintenant d'un accès illimité sans publicité.\n"
                "Retournez dans le groupe pour profiter de votre plan.",
                parse_mode="html"
            )

            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=(
                    "<b>#PAIEMENT_TON</b>\n\n"
                    f"Utilisateur : {user_mention}\n"
                    f"ID : <code>{user_id}</code>\n"
                    f"Plan : <b>{plan_label}</b> ({days} jours)\n"
                    f"Montant : <code>{amount_ton} TON</code>\n"
                    f"TX BOC : <code>{tx_boc[:60]}…</code>\n"
                    f"Expiration : <code>{expiry_str}</code>"
                ),
                parse_mode="html"
            )

        except Exception as e:
            logger.error(f"[WebApp/TON] Erreur grant_premium_plan pour {user_id} : {e}")
            await message.reply_text(
                "<b>Erreur lors de l'activation du plan.</b>\n\n"
                f"Référence transaction : <code>{tx_boc[:40]}</code>\n\n"
                "Contactez le support avec cette référence.",
                parse_mode="html"
            )

    else:
        logger.warning(f"[WebApp] Action inconnue '{action}' reçue de {user_id}")
