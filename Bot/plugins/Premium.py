# plugins/Premium.py

import logging
import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from pyrogram.enums import ParseMode
from database.jks_db import (
    grant_premium_plan, revoke_premium, get_user_access,
    get_all_premium_users, PLAN_LABELS, PLAN_PRICES,
    PLAN_DURATIONS, format_expiry, time_remaining
)
from info import ADMINS, LOG_CHANNEL, MINI_APP_URL

logger = logging.getLogger(__name__)

PLAN_ORDER = ["bronze", "argent", "or", "platine", "diamant", "adamantide"]


# ── Commande /premium ──────────────────────────────────────────────────────────

@Client.on_message(filters.command("premium") & filters.private)
async def premium_command(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    # ── Mode admin : /premium {user_id} ───────────────────────────────────────
    if user_id in ADMINS and len(args) == 2:
        try:
            target_id = int(args[1])
        except ValueError:
            await message.reply_text(
                "<b>Utilisation incorrecte.</b>\n\n"
                "Usage : <code>/premium {identifiant_utilisateur}</code>",
                parse_mode=ParseMode.HTML
            )
            return

        try:
            target_user = await client.get_users(target_id)
            target_mention = target_user.mention
        except Exception:
            target_mention = f"<code>{target_id}</code>"

        access = await get_user_access(target_id)
        current_plan = access.get("plan", "free")
        premium_expiry = access.get("premium_expiry")
        session_expiry = access.get("session_expiry")

        if access["access_type"] == "premium":
            status_line = (
                f"Plan actif : <b>{PLAN_LABELS.get(current_plan, current_plan)}</b>\n"
                f"Expiration : <code>{format_expiry(premium_expiry)}</code>\n"
                f"Temps restant : <b>{time_remaining(premium_expiry)}</b>"
            )
        elif access["access_type"] == "session":
            status_line = (
                f"Session gratuite active\n"
                f"Expiration : <code>{format_expiry(session_expiry)}</code>\n"
                f"Temps restant : <b>{time_remaining(session_expiry)}</b>"
            )
        else:
            status_line = "Aucun accès actif."

        text = (
            f"<b>Gestion du compte</b>\n\n"
            f"Utilisateur : {target_mention}\n"
            f"ID : <code>{target_id}</code>\n\n"
            f"{status_line}\n\n"
            f"<b>Choisissez le plan à attribuer :</b>"
        )

        buttons = _build_admin_buttons(target_id)
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
        return

    # ── Mode utilisateur normal : /premium ─────────────────────────────────────
    access = await get_user_access(user_id)
    current_plan = access.get("plan", "free")
    premium_expiry = access.get("premium_expiry")
    session_expiry = access.get("session_expiry")

    if access["access_type"] == "premium":
        header = (
            f"<b>Votre plan actuel : {PLAN_LABELS.get(current_plan, current_plan)}</b>\n"
            f"Expiration : <code>{format_expiry(premium_expiry)}</code>\n"
            f"Temps restant : <b>{time_remaining(premium_expiry)}</b>\n\n"
        )
    elif access["access_type"] == "session":
        header = (
            f"<b>Session gratuite active</b>\n"
            f"Expiration : <code>{format_expiry(session_expiry)}</code>\n"
            f"Temps restant : <b>{time_remaining(session_expiry)}</b>\n\n"
        )
    else:
        header = (
            "<b>Vous n'avez pas de session active.</b>\n\n"
        )

    plans_text = "<b>ᴘʟᴀɴꜱ ᴅɪꜱᴘᴏɴɪʙʟᴇꜱ :</b>\n\n"
    for plan in PLAN_ORDER:
        label = PLAN_LABELS[plan]
        prices = PLAN_PRICES[plan]
        plans_text += (
            f"<b>{label}</b>\n"
            f"   {prices['fcfa']} ꜰᴄꜰᴀ  |  {prices['cdf']} ᴄᴅꜰ  |  {prices['usd']} $  |  ⭐ {prices['stars']} Stars\n\n"
        )

    footer = (
        "ᴏᴜᴠʀᴇᴢ ʟᴀ ᴍɪɴɪ ᴀᴘᴘ ᴘᴏᴜʀ ᴀᴄʜᴇᴛᴇʀ ᴜɴ ᴘʟᴀɴ ᴠɪᴀ <b>ᴛᴏɴ ᴄᴏɴɴᴇᴄᴛ</b>\n"
        "ᴏᴜ ʀᴇɢᴀʀᴅᴇᴢ ᴜɴᴇ ᴘᴜʙ ᴘᴏᴜʀ ᴏʙᴛᴇɴɪʀ <b>1 ʜᴇᴜʀᴇ ᴅ'ᴀᴄᴄᴇꜱ ɢʀᴀᴛᴜɪᴛ</b>.\n\n"
        "ᴘᴏᴜʀ ᴘᴀʏᴇʀ ᴇɴ <b>ᴛᴇʟᴇɢʀᴀᴍ Stars ⭐</b>, ᴇɴ <b>ᴍᴏʙɪʟᴇ ᴍᴏɴᴇʏ</b> ᴏᴜ ᴇɴ <b>ᴜꜱᴅᴛ</b>, ᴄᴏɴᴛᴀᴄᴛᴇᴢ ʟᴇ ꜱᴜᴘᴘᴏʀᴛ."
    )

    await message.reply_text(
        header + plans_text + footer,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "ᴏᴜᴠʀɪʀ ᴊᴇꜱꜱɪᴋᴀ ꜱᴇᴀʀᴄʜ",
                web_app={"url": MINI_APP_URL}
            )
        ]]),
        parse_mode=ParseMode.HTML
    )


# ── Callback admin — attribution d'un plan ─────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^jksprem_(.+)_(\d+)$"))
async def callback_admin_plan(client: Client, query: CallbackQuery):
    """
    Format callback_data : jksprem_{plan}_{target_user_id}
    plan peut être : bronze | argent | or | platine | diamant | adamantide | revoke
    """
    if query.from_user.id not in ADMINS:
        await query.answer("Accès refusé.", show_alert=True)
        return

    data_parts = query.data.split("_")
    # jksprem_bronze_123456 → ['jksprem', 'bronze', '123456']
    plan = data_parts[1]
    target_id = int(data_parts[2])

    # ── Retirer le premium ────────────────────────────────────────────────────
    if plan == "revoke":
        await revoke_premium(target_id)
        await query.answer("Premium retiré avec succès.", show_alert=True)
        await query.message.edit_text(
            f"<b>Plan retiré.</b>\n\nUtilisateur : <code>{target_id}</code>",
            parse_mode=ParseMode.HTML
        )
        try:
            await client.send_message(
                chat_id=target_id,
                text=(
                    "<b>Votre abonnement premium a été retiré.</b>\n\n"
                    "Vous devrez désormais regarder une publicité pour accéder aux fichiers.\n\n"
                    "Tapez /premium pour consulter les plans disponibles."
                ),
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=(
                "<b>#PREMIUM_RETIRÉ</b>\n\n"
                f"Utilisateur : <code>{target_id}</code>\n"
                f"Retiré par : {query.from_user.mention}"
            ),
            parse_mode=ParseMode.HTML
        )
        return

    # ── Attribuer un plan ─────────────────────────────────────────────────────
    try:
        expiry = await grant_premium_plan(target_id, plan)
        expiry_str = format_expiry(expiry)
        label = PLAN_LABELS.get(plan, plan)

        await query.answer(f"Plan {label} attribué avec succès.", show_alert=True)
        await query.message.edit_text(
            f"<b>Plan attribué.</b>\n\n"
            f"Utilisateur : <code>{target_id}</code>\n"
            f"Plan : <b>{label}</b>\n"
            f"Expiration : <code>{expiry_str}</code>",
            parse_mode=ParseMode.HTML
        )

        try:
            await client.send_message(
                chat_id=target_id,
                text=(
                    f"<b>Félicitations ! Votre plan {label} est maintenant actif.</b>\n\n"
                    f"Vous bénéficiez d'un accès illimité aux fichiers sans publicité.\n"
                    f"Expiration : <code>{expiry_str}</code>\n\n"
                    f"Profitez bien de JessiKaSearch !"
                ),
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=(
                "<b>#PREMIUM_ATTRIBUÉ</b>\n\n"
                f"Utilisateur : <code>{target_id}</code>\n"
                f"Plan : <b>{label}</b>\n"
                f"Expiration : <code>{expiry_str}</code>\n"
                f"Attribué par : {query.from_user.mention}"
            ),
            parse_mode=ParseMode.HTML
        )

    except ValueError as e:
        await query.answer(str(e), show_alert=True)


# ── Commande /premium_users (admin) ───────────────────────────────────────────

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_users_list(client: Client, message: Message):
    users = await get_all_premium_users()

    if not users:
        await message.reply_text(
            "<b>Aucun utilisateur premium actif pour le moment.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    text = f"<b>Utilisateurs premium actifs : {len(users)}</b>\n\n"
    for user in users[:30]:  # limite à 30 pour éviter les messages trop longs
        uid = user.get("id")
        plan = user.get("premium_plan", "inconnu")
        expiry = user.get("premium_expiry")
        label = PLAN_LABELS.get(plan, plan)
        remaining = time_remaining(expiry) if expiry else "—"
        text += f"• <code>{uid}</code> — {label} — {remaining}\n"

    if len(users) > 30:
        text += f"\n<i>... et {len(users) - 30} autres.</i>"

    await message.reply_text(text, parse_mode=ParseMode.HTML)


# ── Helper : construction des boutons admin ────────────────────────────────────

def _build_admin_buttons(target_id: int) -> list:
    buttons = []
    for plan in PLAN_ORDER:
        label = PLAN_LABELS[plan]
        prices = PLAN_PRICES[plan]
        buttons.append([
            InlineKeyboardButton(
                f"{label} — {prices['fcfa']} FCFA / {prices['usd']} $",
                callback_data=f"jksprem_{plan}_{target_id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            "ʀᴇᴛɪʀᴇʀ ʟᴇ ᴘʀᴇᴍɪᴜᴍ",
            callback_data=f"jksprem_revoke_{target_id}"
        )
    ])
    return buttons
