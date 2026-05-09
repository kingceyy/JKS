import re
import os
from os import environ, getenv
from Script import script

# Utility functions
id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# ============================
# Bot Information Configuration
# ============================
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '37641587'))
API_HASH = environ.get('API_HASH', '9bce1167e828939f39452795e56202a9')
BOT_TOKEN = environ.get('BOT_TOKEN', "8330516294:AAGoXGZ1_mO50GfZgaAWLUoqR35BI54-6_o")

# ============================
# Bot Settings Configuration
# ============================
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))

PICS = (environ.get('PICS', 'https://i.ibb.co/mfbQNfq/80395be46a7c.jpg')).split()
NOR_IMG = environ.get("NOR_IMG", "https://envs.sh/Wdj.jpg")
MELCOW_VID = environ.get("MELCOW_VID", "https://envs.sh/Wdj.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://envs.sh/Wdj.jpg")
SUBSCRIPTION = (environ.get('SUBSCRIPTION', 'https://i.ibb.co/mfbQNfq/80395be46a7c.jpg'))
FSUB_PICS = (environ.get('FSUB_PICS', 'https://i.ibb.co/mfbQNfq/80395be46a7c.jpg')).split()

# ============================
# Admin, Channels & Users Configuration
# ============================
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8467461906').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001619818259').split()]
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003665809003'))
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', '-1003340962000'))
MOVIE_UPDATE_CHANNEL = int(environ.get('MOVIE_UPDATE_CHANNEL', '-1003062493614'))
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-1003340962000'))
auth_channel = environ.get('AUTH_CHANNEL', '-1003062493614')
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '').split()]
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-1003981432932')
reqst_channel = environ.get('REQST_CHANNEL_ID', '')
AUTH_CHANNEL = [int(fch) if id_pattern.search(fch) else fch for fch in environ.get('AUTH_CHANNEL', '-1003062493614').split()]
MULTI_FSUB = [int(channel_id) for channel_id in environ.get('MULTI_FSUB', '-1003062493614').split() if re.match(r'^-?\d+$', channel_id)]


# ============================
# Payment Configuration
# ============================
QR_CODE = environ.get('QR_CODE', 'https://i.ibb.co/DH1LCwxR/2c061602eb38.jpg')
OWNER_UPI_ID = environ.get('OWNER_UPI_ID', '@fam')

MINI_APP_URL = environ.get('MINI_APP_URL', 'https://t.me/JessiKaSearchBot/app')

#Auto approve 
CHAT_ID = [int(app_chat_id) if id_pattern.search(app_chat_id) else app_chat_id for app_chat_id in environ.get('CHAT_ID', '').split()]
TEXT = environ.get("APPROVED_WELCOME_TEXT", "<b>{mention},\n\nᴠᴏᴛʀᴇ ᴅᴇᴍᴀɴᴅᴇ ᴘᴏᴜʀ ʀᴇᴊᴏɪɴᴅʀᴇ {title} ᴀ ᴇ́ᴛᴇ́ ᴀᴄᴄᴇᴘᴛᴇ́ᴇ.\n\n‣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @JessiKaDev</b>")
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()


# ============================
# MongoDB Configuration
# ============================
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://sohamdebnathwg:Ai8RyKuaak7awEuN@cluster0.wks1ea5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_URI2 = environ.get('DATABASE_URI2', "mongodb+srv://altof2:123Bonjoure@cluster0.s1suq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "yato")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Lucy_files')

# ============================
# Movie Notification & Update Settings
# ============================
MOVIE_UPDATE_NOTIFICATION = bool(environ.get('MOVIE_UPDATE_NOTIFICATION', True))
# FIX: utilisait bool() qui retourne toujours True même si la valeur est "False"
IMAGE_FETCH = is_enabled(environ.get('IMAGE_FETCH', "True"), True)
CAPTION_LANGUAGES = ["fr", "French", "VF", "Vostfr", "Vo", "Français", "Vost", "Jp"]

# ============================
# Verification Settings
# ============================
VERIFY = bool(environ.get('VERIFY', False))
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 24))
VERIFIED_LOG = int(environ.get('VERIFIED_LOG', '-1003340962000'))
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', 'https://t.me/JessiKaSearch/50')

# ============================
# Link Shortener Configuration
# ============================
IS_SHORTLINK = bool(environ.get('IS_SHORTLINK', False))
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'inshorturl.com')
SHORTLINK_API = environ.get('SHORTLINK_API', '')
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/JessiKaSearch/50')
IS_TUTORIAL = bool(environ.get('IS_TUTORIAL', True))

# ============================
# Channel & Group Links Configuration
# ============================
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/JessiKaSearchGrp')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/JessiKaSearch')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/kingcey')
MOVIE_UPDATE_CHANNEL_LNK = environ.get('MOVIE_UPDATE_CHANNEL_LNK', 'https://t.me/JessiKaSearch')
OWNERID = int(os.environ.get('OWNERID', '8467461906'))

# ============================
# User Configuration
# ============================
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
PREMIUM_USER = [int(user) if id_pattern.search(user) else user for user in environ.get('PREMIUM_USER', '').split()]

# ============================
# Miscellaneous Configuration
# ============================
NO_RESULTS_MSG = bool(environ.get("NO_RESULTS_MSG", True))
MAX_B_TN = environ.get("MAX_B_TN", "15")
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'JessiKa - Recherche')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/+Fm--PVmdy9E4Mjc0')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "True")), True)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)
DELETE_TIME = int(environ.get("DELETE_TIME", "300"))
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "False")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '-1003340962000')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "False")), False)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), True)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)
PM_SEARCH = bool(environ.get('PM_SEARCH', False))
EMOJI_MODE = bool(environ.get('EMOJI_MODE', True))

# ============================
# Bot Configuration
# ============================
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
LANGUAGES = ["fr", "French", "VF", "Vostfr", "Vo", "Français", "Vost", "Jp"]
QUALITIES = ["360P", "", "480P", "", "720P", "", "1080P", "", "1440P", "", "2160P", ""]
SEASONS = ["saison 1" , "saison 2" , "saison 3" , "saison 4", "saison 5" , "saison 6" , "saison 7" , "saison 8" , "saison 9" , "saison 10"]

# ============================
# Server & Web Configuration
# ============================
STREAM_MODE = bool(environ.get('STREAM_MODE', True))

NO_PORT = bool(environ.get('NO_PORT', False))
APP_NAME = None
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = environ.get('APP_NAME')
else:
    ON_HEROKU = False
BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', 'https://experienced-marnie-imbd-db361783.koyeb.app'))
FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else APP_NAME+'.herokuapp.com'
URL = "https://{}/".format(FQDN) if ON_HEROKU or NO_PORT else "https://{}/".format(FQDN, PORT)
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
WORKERS = int(environ.get('WORKERS', '4'))
SESSION_NAME = str(environ.get('SESSION_NAME', 'kingcey'))
MULTI_CLIENT = False
name = str(environ.get('name', 'Deendayal'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = str(getenv('APP_NAME'))
else:
    ON_HEROKU = False
HAS_SSL = bool(getenv('HAS_SSL', True))
if HAS_SSL:
    URL = "https://{}/".format(FQDN)
else:
    URL = "http://{}/".format(FQDN)

# ============================
# Reactions Configuration
# ============================
REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"]



# ============================
# Command admin
# ============================
commands = [
    """• /system - <code>ɪɴғᴏʀᴍᴀᴛɪᴏɴs sʏsᴛèᴍᴇ</code>
• /del_msg - <code>sᴜᴘᴘʀɪᴍᴇʀ ʟᴀ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴅᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ᴅᴇ ɴᴏᴍs ᴅᴇ ғɪᴄʜɪᴇʀs</code>
• /movie_update - <code>ᴀᴄᴛɪᴠᴇʀ/ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ sᴇʟᴏɴ ʙᴇsᴏɪɴ</code>
• /pm_search - <code>ᴀᴄᴛɪᴠᴇʀ/ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ ʟᴀ ʀᴇᴄʜᴇʀᴄʜᴇ ᴇɴ ᴍᴘ</code>
• /logs - <code>ᴏʙᴛᴇɴɪʀ ʟᴇs ᴅᴇʀɴɪèʀᴇs ᴇʀʀᴇᴜʀs</code>
• /delete - <code>sᴜᴘᴘʀɪᴍᴇʀ ᴜɴ ғɪᴄʜɪᴇʀ sᴘᴇ́ᴄɪғɪǫᴜᴇ ᴅᴇ ʟᴀ ʙᴅ</code>
• /users - <code>ᴏʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs ᴇᴛ ɪᴅs</code>
• /chats - <code>ᴏʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴄʜᴀᴛs ᴇᴛ ɪᴅs</code>
• /leave  - <code>ǫᴜɪᴛᴛᴇʀ ᴜɴ ᴄʜᴀᴛ</code>
• /disable  -  <code>ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ ᴜɴ ᴄʜᴀᴛ</code>""",

    """• /ban  - <code>ʙᴀɴɴɪʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ</code>
• /unban  - <code>ᴅᴇ́ʙᴀɴɴɪʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ</code>
• /channel - <code>ᴏʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ɢʀᴏᴜᴘᴇs ᴄᴏɴɴᴇᴄᴛᴇ́s</code>
• /broadcast - <code>ᴇɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴛᴏᴜs ʟᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs</code>
• /grp_broadcast - <code>ᴇɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴛᴏᴜs ʟᴇs ɢʀᴏᴜᴘᴇs ᴄᴏɴɴᴇᴄᴛᴇ́s</code>
• /clear_junk -  <code>ɴᴇᴛᴛᴏʏᴇʀ ʟᴇs ᴅᴏɴɴᴇ́ᴇs ɪɴᴜᴛɪʟᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs</code>
• /junk_group -  <code>ɴᴇᴛᴛᴏʏᴇʀ ʟᴇs ᴅᴏɴɴᴇ́ᴇs ɪɴᴜᴛɪʟᴇs ɢʀᴏᴜᴘᴇs</code>
• /gfilter - <code>ᴀᴊᴏᴜᴛᴇʀ ᴜɴ ғɪʟᴛʀᴇ ɢʟᴏʙᴀʟ</code>
• /gfilters - <code>ᴠᴏɪʀ ᴛᴏᴜs ʟᴇs ғɪʟᴛʀᴇs ɢʟᴏʙᴀᴜx</code>
• /delg - <code>sᴜᴘᴘʀɪᴍᴇʀ ᴜɴ ғɪʟᴛʀᴇ ɢʟᴏʙᴀʟ sᴘᴇ́ᴄɪғɪǫᴜᴇ</code>
• /delallg - <code>sᴜᴘᴘʀɪᴍᴇʀ ᴛᴏᴜs ʟᴇs ғɪʟᴛʀᴇs ɢʟᴏʙᴀᴜx ᴅᴇ ʟᴀ ʙᴅ</code>
• /deletefiles - <code>sᴜᴘᴘʀɪᴍᴇʀ ʟᴇs ғɪᴄʜɪᴇʀs CᴀᴍRɪᴘ ᴇᴛ PʀᴇDVD ᴅᴇ ʟᴀ ʙᴅ</code>
• /send - <code>ᴇɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴘʀᴇ́ᴄɪs</code>""",

    """• /add_premium - <code>ᴀᴊᴏᴜᴛᴇʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴇɴ ᴘʀᴇᴍɪᴜᴍ</code>
• /remove_premium - <code>ʀᴇᴛɪʀᴇʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴅᴜ ᴘʀᴇᴍɪᴜᴍ</code>
• /premium_users - <code>ᴏʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs ᴘʀᴇᴍɪᴜᴍ</code>
• /get_premium - <code>ᴏʙᴛᴇɴɪʀ ʟᴇs ɪɴғᴏs ᴅ'ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴘʀᴇᴍɪᴜᴍ</code>
• /restart - <code>ʀᴇᴅᴇ́ᴍᴀʀʀᴇʀ ʟᴇ ʙᴏᴛ</code>"""
]

# ============================
# Command Bot
# ============================
Bot_cmds = {
    "start": "Dᴇ́ᴍᴀʀʀᴇʀ ʟᴇ ʙᴏᴛ",
    "alive": "Vᴇ́ʀɪғɪᴇʀ sɪ ʟᴇ ʙᴏᴛ ᴇsᴛ ᴇɴ ʟɪɢɴᴇ",
    "paramètres": "Mᴏᴅɪғɪᴇʀ ʟᴇs ᴘᴀʀᴀᴍèᴛʀᴇs",
    "id": "Oʙᴛᴇɴɪʀ ᴜɴ ɪᴅ Tᴇʟᴇɢʀᴀᴍ",
    "info": "Oʙᴛᴇɴɪʀ ʟᴇs ɪɴғᴏs ᴅ'ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ",
    "system": "Iɴғᴏʀᴍᴀᴛɪᴏɴs sʏsᴛèᴍᴇ",
    "del_msg": "Sᴜᴘᴘʀɪᴍᴇʀ ʟᴀ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴅᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ",
    "movie_update": "Aᴄᴛɪᴠᴇʀ/ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ sᴇʟᴏɴ ʙᴇsᴏɪɴ",
    "pm_search": "Aᴄᴛɪᴠᴇʀ/ᴅᴇ́sᴀᴄᴛɪᴠᴇʀ ʟᴀ ʀᴇᴄʜᴇʀᴄʜᴇ ᴇɴ ᴍᴘ",
    "trendlist": "Oʙᴛᴇɴɪʀ ʟᴇ ᴛᴏᴘ ᴅᴇs ʀᴇᴄʜᴇʀᴄʜᴇs ᴛᴇɴᴅᴀɴᴄᴇ",
    "logs": "Oʙᴛᴇɴɪʀ ʟᴇs ᴅᴇʀɴɪèʀᴇs ᴇʀʀᴇᴜʀs",
    "delete": "Sᴜᴘᴘʀɪᴍᴇʀ ᴜɴ ғɪᴄʜɪᴇʀ sᴘᴇ́ᴄɪғɪǫᴜᴇ ᴅᴇ ʟᴀ ʙᴅ",
    "users": "Oʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs",
    "chats": "Oʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴄʜᴀᴛs",
    "leave": "Qᴜɪᴛᴛᴇʀ ᴜɴ ᴄʜᴀᴛ",
    "disable": "Dᴇ́sᴀᴄᴛɪᴠᴇʀ ᴜɴ ᴄʜᴀᴛ",
    "ban": "Bᴀɴɴɪʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ",
    "unban": "Dᴇ́ʙᴀɴɴɪʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ",
    "channel": "Oʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ɢʀᴏᴜᴘᴇs ᴄᴏɴɴᴇᴄᴛᴇ́s",
    "broadcast": "Eɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴛᴏᴜs ʟᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs",
    "grp_broadcast": "Eɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴛᴏᴜs ʟᴇs ɢʀᴏᴜᴘᴇs",
    "clear_junk": "Nᴇᴛᴛᴏʏᴇʀ ʟᴇs ᴅᴏɴɴᴇ́ᴇs ɪɴᴜᴛɪʟᴇs ᴜᴛɪʟɪsᴀᴛᴇᴜʀs",
    "junk_group": "Nᴇᴛᴛᴏʏᴇʀ ʟᴇs ᴅᴏɴɴᴇ́ᴇs ɪɴᴜᴛɪʟᴇs ɢʀᴏᴜᴘᴇs",
    "gfilter": "Aᴊᴏᴜᴛᴇʀ ᴜɴ ғɪʟᴛʀᴇ ɢʟᴏʙᴀʟ",
    "gfilters": "Vᴏɪʀ ᴛᴏᴜs ʟᴇs ғɪʟᴛʀᴇs ɢʟᴏʙᴀᴜx",
    "delg": "Sᴜᴘᴘʀɪᴍᴇʀ ᴜɴ ғɪʟᴛʀᴇ ɢʟᴏʙᴀʟ sᴘᴇ́ᴄɪғɪǫᴜᴇ",
    "delallg": "Sᴜᴘᴘʀɪᴍᴇʀ ᴛᴏᴜs ʟᴇs ғɪʟᴛʀᴇs ɢʟᴏʙᴀᴜx",
    "deletefiles": "Sᴜᴘᴘʀɪᴍᴇʀ ʟᴇs ғɪᴄʜɪᴇʀs CᴀᴍRɪᴘ ᴇᴛ PʀᴇDVD",
    "send": "Eɴᴠᴏʏᴇʀ ᴜɴ ᴍᴇssᴀɢᴇ ᴀ̀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴘʀᴇ́ᴄɪs",
    "add_premium": "Aᴊᴏᴜᴛᴇʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴇɴ ᴘʀᴇᴍɪᴜᴍ",
    "remove_premium": "Rᴇᴛɪʀᴇʀ ᴜɴ ᴜᴛɪʟɪsᴀᴛᴇᴜʀ ᴅᴜ ᴘʀᴇᴍɪᴜᴍ",
    "premium_users": "Oʙᴛᴇɴɪʀ ʟᴀ ʟɪsᴛᴇ ᴅᴇs ᴘʀᴇᴍɪᴜᴍs",
    "get_premium": "Oʙᴛᴇɴɪʀ ʟᴇs ɪɴғᴏs ᴅ'ᴜɴ ᴘʀᴇᴍɪᴜᴍ",
    "restart": "Rᴇᴅᴇ́ᴍᴀʀʀᴇʀ ʟᴇ ʙᴏᴛ"
}




# ============================
# Logs Configuration
# ============================
LOG_STR = "Configurations actuelles du bot :-\n"
LOG_STR += ("Résultats IMDB activés, le bot affichera les détails IMDB pour vos recherches.\n" if IMDB else "Résultats IMDB désactivés.\n")
LOG_STR += ("P_TTI_SHOW_OFF activé, les utilisateurs seront redirigés vers /start en MP au lieu de recevoir le fichier directement.\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF désactivé, les fichiers seront envoyés en MP directement.\n")
LOG_STR += ("SINGLE_BUTTON activé, le nom et la taille du fichier seront affichés dans un seul bouton.\n" if SINGLE_BUTTON else "SINGLE_BUTTON désactivé, le nom et la taille du fichier seront affichés sur deux boutons séparés.\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION activé avec la valeur {CUSTOM_FILE_CAPTION}, vos fichiers seront envoyés avec cette légende personnalisée.\n" if CUSTOM_FILE_CAPTION else "Aucun CUSTOM_FILE_CAPTION trouvé, les légendes par défaut seront utilisées.\n")
LOG_STR += ("Description IMDB longue activée.\n" if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION désactivé, le résumé sera court.\n")
LOG_STR += ("Mode correction orthographique activé, le bot suggérera des films similaires en cas de faute de frappe.\n" if SPELL_CHECK_REPLY else "Mode correction orthographique désactivé.\n")
