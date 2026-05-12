
import re, math, logging, secrets, mimetypes, time
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from TechVJ.bot import multi_clients, work_loads, TechVJBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("JessiKa Search Bot")

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )



# ══════════════════════════════════════════════════════════════════════════════
#  API Mini App JessiKa — endpoints consommes par la Mini App React
# ══════════════════════════════════════════════════════════════════════════════

import hashlib
import hmac
import json as _json
from urllib.parse import parse_qs, unquote
from database.jks_db import (
    get_user_access, get_search_stats, get_recent_searches,
    grant_free_session, grant_premium_plan, PLAN_LABELS as JKS_PLAN_LABELS
)

VALID_PLANS = {"bronze", "argent", "or", "platine", "diamant", "adamantide"}

CORS_HEADERS_GET = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Init-Data",
}

CORS_HEADERS_POST = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Init-Data",
}


def _validate_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    Valide la signature Telegram WebApp initData (HMAC-SHA256).
    Retourne le dict user si valide, None sinon.
    """
    if not init_data:
        return None
    try:
        params = parse_qs(init_data, keep_blank_values=True)
        hash_val = params.pop("hash", [None])[0]
        if not hash_val:
            return None
        data_check = "\n".join(
            f"{k}={v[0]}" for k, v in sorted(params.items())
        )
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            return None
        auth_date = int(params.get("auth_date", ["0"])[0])
        if time.time() - auth_date > 3600:
            return None
        user_raw = params.get("user", ["{}"])[0]
        return _json.loads(unquote(user_raw))
    except Exception:
        return None


# -- GET /api/user/me --

@routes.options("/api/user/me")
async def api_user_me_options(request: web.Request):
    return web.Response(headers=CORS_HEADERS_GET)


@routes.get("/api/user/me")
async def api_user_me(request: web.Request):
    """
    Retourne les donnees de l'utilisateur pour la Mini App React.
    """
    from info import BOT_TOKEN
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user = _validate_telegram_init_data(init_data, BOT_TOKEN)
    if not user:
        return web.json_response(
            {"error": "Unauthorized: invalid or expired initData"},
            status=401, headers=CORS_HEADERS_GET,
        )
    user_id = int(user.get("id", 0))
    if not user_id:
        return web.json_response({"error": "Invalid user id"}, status=400, headers=CORS_HEADERS_GET)
    try:
        access = await get_user_access(user_id)
        stats = await get_search_stats(user_id)
        recent = await get_recent_searches(user_id, limit=10)
        premium_expiry = access.get("premium_expiry")
        session_expiry = access.get("session_expiry")
        payload = {
            "plan": access.get("plan", "free"),
            "premiumExpiry": premium_expiry.isoformat() if premium_expiry else None,
            "sessionExpiry": session_expiry.isoformat() if session_expiry else None,
            "totalSearches": stats.get("total_searches", 0),
            "weekSearches": stats.get("week_searches", 0),
            "dailySearches": stats.get("daily_searches", [0] * 7),
            "recentSearches": [
                {"query": r["query"], "timestamp": r["timestamp"].isoformat()}
                for r in recent
            ],
        }
        return web.json_response(payload, headers=CORS_HEADERS_GET)
    except Exception as e:
        logging.exception(f"[API /api/user/me] Erreur pour user {user_id}: {e}")
        return web.json_response({"error": "Internal server error"}, status=500, headers=CORS_HEADERS_GET)


# -- POST /api/session/activate --

@routes.options("/api/session/activate")
async def api_session_activate_options(request: web.Request):
    return web.Response(headers=CORS_HEADERS_POST)


@routes.post("/api/session/activate")
async def api_session_activate(request: web.Request):
    """
    Appele par la Mini App apres que l'utilisateur a regarde les 2 pubs.
    """
    from info import BOT_TOKEN
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user = _validate_telegram_init_data(init_data, BOT_TOKEN)
    if not user:
        return web.json_response(
            {"error": "Unauthorized: invalid or expired initData"},
            status=401, headers=CORS_HEADERS_POST,
        )
    user_id = int(user.get("id", 0))
    if not user_id:
        return web.json_response({"error": "Invalid user id"}, status=400, headers=CORS_HEADERS_POST)
    try:
        expiry = await grant_free_session(user_id)
        return web.json_response(
            {"ok": True, "sessionExpiry": expiry.isoformat()},
            headers=CORS_HEADERS_POST,
        )
    except Exception as e:
        logging.exception(f"[API /api/session/activate] Erreur pour user {user_id}: {e}")
        return web.json_response({"error": "Internal server error"}, status=500, headers=CORS_HEADERS_POST)


# -- POST /api/notify --

@routes.options("/api/notify")
async def api_notify_options(request: web.Request):
    return web.Response(headers=CORS_HEADERS_POST)


@routes.post("/api/notify")
async def api_notify(request: web.Request):
    """
    Recoit les notifications de la Mini App (paiement TON etc.).
    """
    from info import BOT_TOKEN, LOG_CHANNEL
    from TechVJ.bot import TechVJBot

    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user = _validate_telegram_init_data(init_data, BOT_TOKEN)
    if not user:
        return web.json_response({"error": "Unauthorized"}, status=401, headers=CORS_HEADERS_POST)

    user_id = int(user.get("id", 0))
    user_first_name = user.get("first_name", str(user_id))

    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400, headers=CORS_HEADERS_POST)

    action = payload.get("action")

    if action == "ton_payment":
        plan_key = payload.get("plan")
        days = payload.get("days")
        tx_boc = payload.get("tx_boc", "N/A")
        amount_ton = payload.get("amount_ton", "?")

        if plan_key not in VALID_PLANS:
            return web.json_response({"error": f"Plan inconnu : {plan_key}"}, status=400, headers=CORS_HEADERS_POST)

        try:
            expiry = await grant_premium_plan(user_id, plan_key)
            plan_label = JKS_PLAN_LABELS.get(plan_key, plan_key)

            try:
                await TechVJBot.send_message(
                    chat_id=LOG_CHANNEL,
                    text=(
                        "<b>#PAIEMENT_TON</b>\n\n"
                        f"Utilisateur : <a href='tg://user?id={user_id}'>{user_first_name}</a>\n"
                        f"ID : <code>{user_id}</code>\n"
                        f"Plan : <b>{plan_label}</b> ({days} jours)\n"
                        f"Montant : <code>{amount_ton} TON</code>\n"
                        f"TX BOC : <code>{str(tx_boc)[:60]}...</code>\n"
                        f"Expiration : <code>{expiry.strftime('%d %b %Y a %H:%M UTC')}</code>"
                    ),
                    parse_mode="html",
                )
            except Exception:
                pass

            try:
                await TechVJBot.send_message(
                    chat_id=user_id,
                    text=(
                        f"<b>Plan {plan_label} active !</b>\n\n"
                        f"Duree : <b>{days} jours</b>\n"
                        f"Expiration : <code>{expiry.strftime('%d %b %Y a %H:%M UTC')}</code>\n\n"
                        "Vous beneficiez maintenant d'un acces illimite sans publicite."
                    ),
                    parse_mode="html",
                )
            except Exception:
                pass

            return web.json_response(
                {"ok": True, "premiumExpiry": expiry.isoformat()},
                headers=CORS_HEADERS_POST,
            )
        except Exception as e:
            logging.exception(f"[API /api/notify] Erreur ton_payment pour {user_id}: {e}")
            return web.json_response({"error": "Internal server error"}, status=500, headers=CORS_HEADERS_POST)

    return web.json_response({"ok": True, "action": action}, headers=CORS_HEADERS_POST)
