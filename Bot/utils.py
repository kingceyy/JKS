import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import *
# Cinemagoer remplacé par TMDB
import asyncio
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram import enums
from typing import Union
from Script import script
import pytz
import random 
import re
import os
from datetime import datetime, date, time, timedelta
import string
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import requests
import aiohttp
from shortzy import Shortzy
import http.client
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

# imdb = Cinemagoer() — remplacé par TMDB
TOKENS = {}
VERIFIED = {}
BANNED = {}
SECOND_SHORTENER = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)


class temp(object):
   
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    B_LINK = None
    GETALL = {}
    SHORT = {}
    SETTINGS = {}
    IMDB_CAP = {}
    VERIFY = {}


async def is_req_subscribed(bot, query):
    if await db.find_join_req(query.from_user.id):
        return True
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False

async def is_subscribed(bot, query, channels):
    btn = []
    for channel_id in channels:
        try:
            chat = await bot.get_chat(int(channel_id))
            await bot.get_chat_member(channel_id, query.from_user.id)
        except UserNotParticipant:
            btn.append(
                [InlineKeyboardButton(f'❤️ {chat.title}', url=chat.invite_link)]
            )
        except Exception as e:
            pass
    return btn

async def is_check_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False
    
async def get_status(bot_id):
    try:
        return await db.movie_update_status(bot_id) or False  
    except Exception as e:
        logging.error(f"Error in get_movie_update_status: {e}")
        return False  

    
TMDB_API_KEY = "f2bed62b5977bce26540055276d0046c"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/original"

async def get_poster(query, bulk=False, id=False, file=None):
    try:
        import aiohttp
    except ImportError:
        import requests as _req

        def _sync_get(url, params):
            r = _req.get(url, params=params, timeout=10)
            return r.json() if r.ok else None

        async def _get(url, params):
            return _sync_get(url, params)
    else:
        async def _get(url, params):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    return await r.json() if r.status == 200 else None

    # Extraire l'année depuis la query ou le nom de fichier
    title = (query.strip()) if not id else query
    year = None
    if not id:
        yr = re.findall(r'[1-2]\d{3}', query)
        if yr:
            year = yr[0]
            title = query.replace(year, "").strip()
        elif file:
            yr = re.findall(r'[1-2]\d{3}', file)
            if yr:
                year = yr[0]

    if id:
        # id TMDB direct
        tmdb_id = query
        # Essayer film puis série
        for media in ("movie", "tv"):
            data = await _get(f"{TMDB_BASE_URL}/{media}/{tmdb_id}", {
                "api_key": TMDB_API_KEY,
                "language": "fr-FR",
                "append_to_response": "credits,external_ids"
            })
            if data and data.get("id"):
                return await _build_result(data, media, _get)
        return None

    # Recherche multi (films + séries)
    params = {"api_key": TMDB_API_KEY, "query": title, "language": "fr-FR"}
    if year:
        params["year"] = year
    data = await _get(f"{TMDB_BASE_URL}/search/multi", params)
    if not data or not data.get("results"):
        # Retry sans l'année
        params.pop("year", None)
        data = await _get(f"{TMDB_BASE_URL}/search/multi", params)
    if not data or not data.get("results"):
        return None

    results = [r for r in data["results"] if r.get("media_type") in ("movie", "tv")]
    if not results:
        results = data["results"]
    if not results:
        return None

    if bulk:
        return results

    best = results[0]
    media_type = best.get("media_type", "movie")
    tmdb_id = best["id"]

    detail = await _get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}", {
        "api_key": TMDB_API_KEY,
        "language": "fr-FR",
        "append_to_response": "credits,external_ids"
    })
    if not detail:
        return None

    return await _build_result(detail, media_type, _get)


async def _build_result(detail, media_type, _get):
    # Titre
    title = detail.get("title") or detail.get("name") or "N/A"

    # Année / date de sortie
    release = detail.get("release_date") or detail.get("first_air_date") or ""
    year = release[:4] if release else "N/A"

    # Genres
    genres = ", ".join(g["name"] for g in detail.get("genres", []))

    # Note et votes
    rating = str(round(detail.get("vote_average", 0), 1))
    votes = str(detail.get("vote_count", "N/A"))

    # Résumé
    plot = detail.get("overview") or ""
    if not LONG_IMDB_DESCRIPTION and len(plot) > 800:
        plot = plot[:800] + "..."

    # Poster
    poster_path = detail.get("poster_path")
    poster = f"{TMDB_IMG_BASE}{poster_path}" if poster_path else None

    # Durée
    runtime = str(detail.get("runtime") or detail.get("episode_run_time", ["N/A"])[0] if isinstance(detail.get("episode_run_time"), list) else "N/A")

    # Pays
    countries = ", ".join(c.get("name", c.get("iso_3166_1", "")) for c in detail.get("production_countries", []))

    # Langues
    languages = ", ".join(l.get("name", l.get("iso_639_1", "")) for l in detail.get("spoken_languages", []))

    # Cast & crew depuis credits
    credits = detail.get("credits", {})
    cast_list = [p["name"] for p in credits.get("cast", [])[:5]]
    cast = ", ".join(cast_list) if cast_list else "N/A"

    crew = credits.get("crew", [])
    directors = ", ".join(p["name"] for p in crew if p.get("job") == "Director") or "N/A"
    writers = ", ".join(p["name"] for p in crew if p.get("department") == "Writing")[:3*30] or "N/A"
    producers = ", ".join(p["name"] for p in crew if p.get("job") == "Producer")[:3*30] or "N/A"
    composers = ", ".join(p["name"] for p in crew if p.get("department") == "Sound")[:2*30] or "N/A"

    # IMDB ID depuis external_ids
    ext = detail.get("external_ids", {})
    imdb_id = ext.get("imdb_id") or "N/A"
    imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id != "N/A" else f"https://www.themoviedb.org/{'movie' if media_type == 'movie' else 'tv'}/{detail.get('id')}"

    # Saisons (séries)
    seasons = str(detail.get("number_of_seasons", "N/A")) if media_type == "tv" else "N/A"

    # Kind
    kind = "movie" if media_type == "movie" else "tv series"

    return {
        'title': title,
        'votes': votes,
        "aka": detail.get("original_title") or detail.get("original_name") or "N/A",
        "seasons": seasons,
        "box_office": "N/A",
        'localized_title': title,
        'kind': kind,
        "imdb_id": imdb_id,
        "cast": cast,
        "runtime": runtime,
        "countries": countries or "N/A",
        "certificates": "N/A",
        "languages": languages or "N/A",
        "director": directors,
        "writer": writers,
        "producer": producers,
        "composer": composers,
        "cinematographer": "N/A",
        "music_team": "N/A",
        "distributors": "N/A",
        'release_date': release or "N/A",
        'year': year,
        'genres': genres or "N/A",
        'poster': poster,
        'plot': plot or "N/A",
        'rating': rating,
        'url': imdb_url,
    }


async def broadcast_messages(user_id, message):
    try:
        m = await message.copy(chat_id=user_id)
        try:
            await m.pin(both_sides=True)
        except:
            pass
        return True, "Succès"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def broadcast_messages_group(chat_id, message):
    try:
        kd = await message.copy(chat_id=chat_id)
        try:
            await kd.pin()
        except:
            pass
        return True, "Succès"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages_group(chat_id, message)
    except Exception as e:
        return False, "Error"
    
async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]

async def get_paramètres(group_id):
    paramètres = temp.SETTINGS.get(group_id)
    if not paramètres:
        paramètres = await db.get_paramètres(group_id)
        temp.SETTINGS[group_id] = paramètres
    return paramètres
    
async def save_group_paramètres(group_id, key, value):
    current = await get_paramètres(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_paramètres(group_id, current)
    
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)
    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def gfilterparser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"gfilteralert:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"gfilteralert:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f'{int(period_value)}{period_name}')
    return ' '.join(result)  

async def get_shortlink(chat_id, link):
    paramètres = await get_paramètres(chat_id) #fetching paramètres for group
    if 'shortlink' in paramètres.keys():
        URL = paramètres['shortlink']
        API = paramètres['shortlink_api']
    else:
        URL = SHORTLINK_URL
        API = SHORTLINK_API
    if URL.startswith("shorturllink") or URL.startswith("terabox.in") or URL.startswith("urlshorten.in"):
        URL = SHORTLINK_URL
        API = SHORTLINK_API
    if URL == "api.shareus.io":
        # method 1:
        # https = link.split(":")[0] #splitting https or http from link
        # if "http" == https: #if https == "http":
        #     https = "https"
        #     link = link.replace("http", https) #replacing http to https
        # conn = http.client.HTTPSConnection("api.shareus.io")
        # payload = json.dumps({
        #   "api_key": "4c1YTBacB6PTuwogBiEIFvZN5TI3",
        #   "monetization": True,
        #   "destination": link,
        #   "ad_page": 3,
        #   "category": "Entertainment",
        #   "tags": ["trendinglinks"],
        #   "monetize_with_money": False,
        #   "price": 0,
        #   "currency": "INR",
        #   "purchase_note":""
        
        # })
        # headers = {
        #   'Keep-Alive': '',
        #   'Content-Type': 'application/json'
        # }
        # conn.request("POST", "/generate_link", payload, headers)
        # res = conn.getresponse()
        # data = res.read().decode("utf-8")
        # parsed_data = json.loads(data)
        # if parsed_data["status"] == "success":
        #   return parsed_data["link"]
    #method 2
        url = f'https://{URL}/easy_api'
        params = {
            "key": API,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(e)
            return link
    else:
        shortzy = Shortzy(api_key=API, base_site=URL)
        link = await shortzy.convert(link)
        return link
    
async def get_tutorial(chat_id):
    paramètres = await get_paramètres(chat_id) #fetching paramètres for group
    if 'tutorial' in paramètres.keys():
        if paramètres['is_tutorial']:
            TUTORIAL_URL = paramètres['tutorial']
        else:
            TUTORIAL_URL = TUTORIAL
    else:
        TUTORIAL_URL = TUTORIAL
    return TUTORIAL_URL
        
async def get_verify_shorted_link(link):
    API = SHORTLINK_API
    URL = SHORTLINK_URL
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    if URL == "api.shareus.in":
        url = f"https://{URL}/shortLink"
        params = {"token": API,
                  "format": "json",
                  "link": link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'

        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {'api': API,
                  'url': link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data['shortenedUrl']
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/api?api={API}&link={link}'

        except Exception as e:
            logger.error(e)
            return f'{URL}/api?api={API}&link={link}'

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False

async def get_token(bot, userid, link, fileid):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}-{fileid}"
    shortened_verify_url = await get_verify_shorted_link(link)
    return str(shortened_verify_url)

async def get_verify_status(userid):
    status = temp.VERIFY.get(userid)
    if not status:
        status = await db.get_verified(userid)
        temp.VERIFY[userid] = status
    return status
    
async def update_verify_status(userid, date_temp, time_temp):
    status = await get_verify_status(userid)
    status["date"] = date_temp
    status["time"] = time_temp
    temp.VERIFY[userid] = status
    await db.update_verification(userid, date_temp, time_temp)

async def verify_user(bot, userid, token):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    date_var = datetime.now(tz)+timedelta(hours=VERIFY_EXPIRE)
    temp_time = date_var.strftime("%H:%M:%S")
    date_var, time_var = str(date_var).split(" ")
    await update_verify_status(user.id, date_var, temp_time)

async def check_verification(bot, userid):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    curr_time = now.strftime("%H:%M:%S")
    hour1, minute1, second1 = curr_time.split(":")
    curr_time = time(int(hour1), int(minute1), int(second1))
    status = await get_verify_status(user.id)
    date_var = status["date"]
    time_var = status["time"]
    years, month, day = date_var.split('-')
    comp_date = date(int(years), int(month), int(day))
    hour, minute, second = time_var.split(":")
    comp_time = time(int(hour), int(minute), int(second))
    if comp_date<today:
        return False
    else:
        if comp_date == today:
            if comp_time<curr_time:
                return False
            else:
                return True
        else:
            return True
            
async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].lstrip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0
    
async def send_all(bot, userid, files, ident, chat_id, user_name, query):
    paramètres = await get_paramètres(chat_id)
    if 'is_shortlink' in paramètres.keys():
        ENABLE_SHORTLINK = paramètres['is_shortlink']
    else:
        await save_group_paramètres(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    try:
        if ENABLE_SHORTLINK:
            for file in files:
                title = file.file_name
                size = get_size(file.file_size)
                await bot.send_message(chat_id=userid, text=f"<b>Hᴇʏ ᴛʜᴇʀᴇ {user_name} 👋🏽 \n\n✅ Sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғɪʟᴇ ʜᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴇᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ\n\n🗃️ Fɪʟᴇ ɴᴏᴍ : {title}\n🔖 Fɪʟᴇ Sɪᴢᴇ : {size}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Dᴏᴡɴʟᴏᴀᴅ 📥", url=await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"))]]))
        else:
            for file in files:
                    f_caption = file.caption
                    title = file.file_name
                    size = get_size(file.file_size)
                    if CUSTOM_FILE_CAPTION:
                        try:
                            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                                    file_size='' if size is None else size,
                                                                    file_caption='' if f_caption is None else f_caption)
                        except Exception as e:
                            print(e)
                            f_caption = f_caption
                    if f_caption is None:
                        f_caption = f"{title}"
                    await bot.send_cached_media(
                        chat_id=userid,
                        file_id=file.file_id,
                        caption=f_caption,
                        protect_content=True if ident == "filep" else False,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ],[
                                InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/cosmic_freak")
                                ]
                            ]
                        )
                    )
    except UserIsBlocked:
        await query.answer('Veuillez debloquer le bot pour recevoir vos fichiers !', show_alert=True)
    except PeerIdInvalid:
        await query.answer('Demarrez d abord le bot en prive, puis cliquez sur Envoyer tout', show_alert=True)
    except Exception as e:
        await query.answer('Demarrez d abord le bot en prive, puis cliquez sur Envoyer tout', show_alert=True)
        
async def get_cap(paramètres, remaining_seconds, files, query, total_results, search):
    if paramètres["imdb"]:
        IMDB_CAP = temp.IMDB_CAP.get(query.from_user.id)
        if IMDB_CAP:
            cap = IMDB_CAP
            cap+="\n\n<b>📚 <u>Vos fichiers demandes</u> 👇\n</b>"
            for file in files:
                cap += f"<b><a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>📁 [{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"
        else:
            # FIX: IMDB poster forcé — indépendant du toggle admin /paramètres
            imdb = await get_poster(search, file=(files[0]).file_name)
            if imdb:
                TEMPLATE = script.IMDB_TEMPLATE_TXT
                cap = TEMPLATE.format(
                    qurey=search,
                    title=imdb['title'],
                    votes=imdb['votes'],
                    aka=imdb["aka"],
                    seasons=imdb["seasons"],
                    box_office=imdb['box_office'],
                    localized_title=imdb['localized_title'],
                    kind=imdb['kind'],
                    imdb_id=imdb["imdb_id"],
                    cast=imdb["cast"],
                    runtime=imdb["runtime"],
                    countries=imdb["countries"],
                    certificates=imdb["certificates"],
                    languages=imdb["languages"],
                    director=imdb["director"],
                    writer=imdb["writer"],
                    producer=imdb["producer"],
                    composer=imdb["composer"],
                    cinematographer=imdb["cinematographer"],
                    music_team=imdb["music_team"],
                    distributors=imdb["distributors"],
                    release_date=imdb['release_date'],
                    year=imdb['year'],
                    genres=imdb['genres'],
                    poster=imdb['poster'],
                    plot=imdb['plot'],
                    rating=imdb['rating'],
                    url=imdb['url'],
                    remaining_seconds=remaining_seconds,
                    user_mention=message.from_user.mention,
                )
                cap+="\n\n<b>📚 <u>Vos fichiers demandes</u> 👇\n\n</b>"
                for file in files:
                    cap += f"<b><a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"
            else:
                cap = f"<b>🧿 ᴛɪᴛʀᴇ : <code>{search}</code>\n📂 ꜰɪᴄʜɪᴇʀꜱ : <code>{total_results}</code>\n📝 ᴅᴇᴍᴀɴᴅᴇ ᴘᴀʀ : {message.from_user.mention}\n⏰ ʀᴇꜱᴜʟᴛᴀᴛ ᴇɴ : <code>{remaining_seconds} ꜱᴇᴄᴏɴᴅᴇꜱ</code>\n⚜️ ᴠɪᴀ : 👇\n⚡ {message.chat.title}\n</b>"
                cap+="\n\n<b>📚 <u>Vos fichiers demandes</u> 👇\n\n</b>"
                for file in files:
                    cap += f"<b><a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"
    else:
        cap = f"<b>🧿 ᴛɪᴛʀᴇ : <code>{search}</code>\n📂 ꜰɪᴄʜɪᴇʀꜱ : <code>{total_results}</code>\n📝 ᴅᴇᴍᴀɴᴅᴇ ᴘᴀʀ : {query.from_user.mention}\n⚜️ ᴠɪᴀ : 👇\n⚡ JessiKa Search\n</b>"
        cap+="\n\n<b>📚 <u>Vos fichiers demandes</u> 👇\n\n</b>"
        for file in files:
            cap += f"<b><a href='https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}'>📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"
    return cap


async def log_error(client, error_message):
    """Logs errors to the specified LOG_CHANNEL."""
    try:
        await client.send_message(
            chat_id=LOG_CHANNEL, 
            text=f"<b>⚠️ Error Log:</b>\n<code>{error_message}</code>"
        )
    except Exception as e:
        print(f"Failed to log error: {e}")


def get_time(seconds):
    periods = [(' ᴅᴀʏs', 86400), (' ʜᴏᴜʀ', 3600), (' ᴍɪɴᴜᴛᴇ', 60), (' sᴇᴄᴏɴᴅ', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result
