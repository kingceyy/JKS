
import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
from info import *
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums
from pyrogram.errors import *
from typing import Union
from Script import script
from datetime import datetime, date
from typing import List
from database.users_chats_db import db
from database.join_reqs import JoinReqs
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
join_db = JoinReqs
BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
# 'original' = image dans sa resolution native fournie par TMDB (pas de compression/crop)
TMDB_IMAGE_ORIGINAL = "https://image.tmdb.org/t/p/original"
TMDB_IMAGE_FALLBACK = "https://image.tmdb.org/t/p/w1280"  # repli si Telegram refuse le fichier original (>10 Mo)

SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    BOT = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    GETALL = {}
    SHORT = {}
    SETTINGS = {}
    IMDB_CAP = {}


async def pub_is_subscribed(bot, query, channels):
    """
    Vérifie si l'utilisateur est abonné à tous les canaux fsub du groupe.
    Retourne une liste de boutons pour les canaux non rejoints.
    Si la liste est vide → l'utilisateur est abonné à tout.
    """
    btn = []
    if not channels:
        return btn
    # channels peut être une liste ou un seul int
    if not isinstance(channels, (list, tuple)):
        channels = [channels]
    for channel_id in channels:
        is_member = False
        chat = None
        try:
            chat = await bot.get_chat(int(channel_id))
        except Exception as e:
            logger.warning(f"[FSUB] Impossible de récupérer le canal {channel_id}: {e}")
            continue
        try:
            member = await bot.get_chat_member(int(channel_id), query.from_user.id)
            if member.status not in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]:
                is_member = True
        except UserNotParticipant:
            is_member = False
        except Exception as e:
            logger.warning(f"[FSUB] Erreur get_chat_member pour {query.from_user.id} dans {channel_id}: {e}")
            is_member = True  # ne pas bloquer en cas d'erreur inconnue

        if not is_member:
            try:
                invite = chat.invite_link
                if not invite:
                    invite = await bot.export_chat_invite_link(int(channel_id))
                btn.append([InlineKeyboardButton(f'Rejoindre {chat.title}', url=invite)])
            except Exception as e:
                logger.warning(f"[FSUB] Impossible de créer le lien d'invitation pour {channel_id}: {e}")
    return btn


async def is_subscribed(bot, query):
    """
    Vérifie si l'utilisateur est abonné au AUTH_CHANNEL global.
    Retourne True si membre, False sinon.
    """
    if not AUTH_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
        return member.status not in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]
    except UserNotParticipant:
        return False
    except Exception:
        return True  # En cas d'erreur inconnue, ne pas bloquer l'utilisateur

class TMDBResult(dict):
    """Dict enrichi qui expose aussi .movieID en attribut, pour rester compatible
    avec le code existant (misc.py) ecrit a l'origine pour les objets Cinemagoer."""
    @property
    def movieID(self):
        return self.get("movieID", "")


async def _tmdb_get(session, endpoint, params=None):
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    params.setdefault("language", "fr-FR")
    try:
        async with session.get(f"{TMDB_BASE_URL}{endpoint}", params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return None
            return await resp.json()
    except Exception as e:
        logger.warning(f"Erreur requete TMDB ({endpoint}) : {e}")
        return None


def _tmdb_result_year(result):
    date_str = result.get("release_date") or result.get("first_air_date") or ""
    return date_str[:4] if date_str else None


async def get_poster(query, bulk=False, id=False, file=None):
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY manquant : impossible de recuperer les infos du film/serie.")
        return None

    async with aiohttp.ClientSession() as session:
        if not id:
            query = (query.strip()).lower()
            title = query
            year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                title = (query.replace(year, "")).strip()
            elif file is not None:
                year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
                if year:
                    year = list_to_str(year[:1])
            else:
                year = None

            data = await _tmdb_get(session, "/search/multi", {"query": title, "include_adult": "false"})
            if not data or not data.get("results"):
                return None

            results = [r for r in data["results"] if r.get("media_type") in ("movie", "tv")]
            if not results:
                return None

            if year:
                filtered = [r for r in results if _tmdb_result_year(r) == str(year)]
                if not filtered:
                    filtered = results
            else:
                filtered = results

            if bulk:
                bulk_results = []
                for r in filtered[:10]:
                    bulk_results.append(TMDBResult({
                        "title": r.get("title") or r.get("name"),
                        "year": _tmdb_result_year(r),
                        "movieID": f"{r.get('media_type')}:{r.get('id')}",
                    }))
                return bulk_results

            best = filtered[0]
            media_type = best.get("media_type")
            tmdb_id = best.get("id")
        else:
            media_type, tmdb_id = query.split(":", 1)

        movie = await _tmdb_get(
            session,
            f"/{media_type}/{tmdb_id}",
            {"append_to_response": "credits,alternative_titles"},
        )
        if not movie:
            return None

        credits_data = movie.get("credits") or {}
        crew = credits_data.get("crew", [])
        cast_list = credits_data.get("cast", [])

        def crew_names(*jobs):
            names = [c.get("name") for c in crew if c.get("job") in jobs]
            return list_to_str(names[:5])

        title = movie.get("title") or movie.get("name")
        release_date = movie.get("release_date") or movie.get("first_air_date") or "N/A"
        year_value = release_date[:4] if release_date and release_date != "N/A" else "N/A"

        if not LONG_IMDB_DESCRIPTION:
            plot = movie.get("overview") or ""
        else:
            plot = movie.get("overview") or ""
        if plot and len(plot) > 800:
            plot = plot[0:800] + "..."

        # Image paysage (backdrop) en taille originale, demande explicitement.
        # Repli sur le poster (portrait) uniquement si aucun backdrop n'existe.
        backdrop_path = movie.get("backdrop_path")
        poster_path = movie.get("poster_path")
        if backdrop_path:
            poster_url = f"{TMDB_IMAGE_ORIGINAL}{backdrop_path}"
        elif poster_path:
            poster_url = f"{TMDB_IMAGE_ORIGINAL}{poster_path}"
        else:
            poster_url = None

        runtime = movie.get("runtime")
        if not runtime:
            episode_runtimes = movie.get("episode_run_time") or []
            runtime = episode_runtimes[0] if episode_runtimes else "N/A"

        alt_titles = (movie.get("alternative_titles") or {}).get("titles") or (movie.get("alternative_titles") or {}).get("results") or []

        return {
            'title': title,
            'votes': movie.get('vote_count'),
            "aka": list_to_str([a.get("title") for a in alt_titles][:5]),
            "seasons": movie.get("number_of_seasons"),
            "box_office": movie.get("revenue"),
            'localized_title': title,
            'kind': "tv series" if media_type == "tv" else "movie",
            "imdb_id": movie.get("imdb_id") or f"{media_type}:{tmdb_id}",
            "cast": list_to_str([c.get("name") for c in cast_list[:5]]),
            "runtime": runtime,
            "countries": list_to_str([c.get("name") for c in movie.get("production_countries", [])]),
            "certificates": "",
            "languages": list_to_str([l.get("english_name") or l.get("name") for l in movie.get("spoken_languages", [])]),
            "director": crew_names("Director"),
            "writer": crew_names("Writer", "Screenplay"),
            "producer": crew_names("Producer"),
            "composer": crew_names("Original Music Composer"),
            "cinematographer": crew_names("Director of Photography"),
            "music_team": crew_names("Original Music Composer"),
            "distributors": list_to_str([c.get("name") for c in movie.get("production_companies", [])]),
            'release_date': release_date,
            'year': year_value,
            'genres': list_to_str([g.get("name") for g in movie.get("genres", [])]),
            'poster': poster_url,
            'poster_fallback': f"{TMDB_IMAGE_FALLBACK}{backdrop_path or poster_path}" if (backdrop_path or poster_path) else None,
            'plot': plot,
            'rating': str(round(movie.get("vote_average", 0) or 0, 1)),
            'url': f"https://www.themoviedb.org/{media_type}/{tmdb_id}"
        }

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Erreur"
    except Exception as e:
        return False, "Erreur"

async def broadcast_messages_group(chat_id, message):
    try:
        kd = await message.copy(chat_id=chat_id)
        try:
            await kd.pin()
        except:
            pass
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages_group(chat_id, message)
    except Exception as e:
        return False, "Erreur"
    
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

async def get_settings(group_id):
    settings = await db.get_settings(group_id)
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current.update({key: value})
    await db.update_settings(group_id, current)
    
def get_size(size):
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
        time += "Recemment"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "La semaine derniere"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Le mois dernier"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "Il y a longtemps :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "En ligne"
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

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
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



async def send_all(bot, userid, files, ident, chat_id, user_name, query):
    try:
        for file in files:
            f_caption = file["caption"]
            title = file["file_name"]
            size = get_size(file["file_size"])
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name='' if title is None else title,
                        file_size='' if size is None else size,
                        file_caption='' if f_caption is None else f_caption
                    )
                except Exception as e:
                    print(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{title}"
            await bot.send_cached_media(
                chat_id=userid,
                file_id=file["file_id"],
                caption=f_caption,
                protect_content=True if ident == "filep" else False,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton('Groupe de support', url=GRP_LNK),
                        InlineKeyboardButton('Canal de mises a jour', url=CHNL_LNK)
                    ],[
                        InlineKeyboardButton("Proprietaire du bot", url=OWNER_LNK)
                    ]]
                )
            )
    except UserIsBlocked:
        await query.answer('Debloquez le bot !', show_alert=True)
    except PeerIdInvalid:
        await query.answer('Demarrez le bot d\'abord puis cliquez sur Envoyer tout', show_alert=True)
    except Exception as e:
        await query.answer('Demarrez le bot d\'abord puis cliquez sur Envoyer tout', show_alert=True)
        


def clean_filename(file_name: str) -> str:
    """Nettoie le nom de fichier pour l'affichage dans les boutons."""
    name = re.sub(r'\[.*?\]', '', file_name)
    name = re.sub(r'[\.\-]', ' ', name)
    tokens = [x for x in name.split() if not x.startswith('@') and x.strip()]
    return " ".join(tokens)

async def get_cap(settings, remaining_secondes, files, query, total_results, search):
    if settings["imdb"]:
        IMDB_CAP = temp.IMDB_CAP.get(query.from_user.id)
        if IMDB_CAP:
            cap = IMDB_CAP
            cap+="<b>\n\n<u>🍿 Vos fichiers 👇</u></b>\n\n"
            for file in files:
                cap += f"<b>📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {clean_filename(file['file_name'])}\n\n</a></b>"
        else:
            # IMDB toujours activé
            imdb = await get_poster(search, file=(files[0])["file_name"])
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
                    remaining_seconds=remaining_secondes,
                    user_mention=query.from_user.mention,
                )
                cap+="<b>\n\n<u>🍿 Vos fichiers 👇</u></b>\n\n"
                for file in files:
                    cap += f"<b>📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {clean_filename(file['file_name'])}\n\n</a></b>"
    return cap


async def get_secondes(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""
        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:]
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



async def get_seconds(time_string):
    return await get_secondes(time_string)
