import re
from os import environ
from Script import script

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if not value:
        return default
    return value.lower() in ["true", "yes", "1", "enable", "y"]

# Bot
SESSION = environ.get('SESSION', 'JessiKaSearch')
API_ID = int(environ.get('API_ID', '37641587'))
API_HASH = environ.get('API_HASH', '9bce1167e828939f39452795e56202a9')
BOT_TOKEN = environ.get('BOT_TOKEN', "8330516294:AAGoXGZ1_mO50GfZgaAWLUoqR35BI54-6_o")

# Images
PICS = (environ.get('PICS', 'https://i.ibb.co/fdXx6d1w/x.jpg')).split()

# TMDB (remplace Cinemagoer/IMDb, casse depuis avril 2026)
TMDB_API_KEY = environ.get('TMDB_API_KEY', 'f2bed62b5977bce26540055276d0046c')

# Admins et utilisateurs
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8467461906').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

# Canaux et groupes
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003665809003'))
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002794593683').split()]

# Force subscribe
REQUEST_TO_JOIN_MODE = is_enabled(environ.get('REQUEST_TO_JOIN_MODE', 'False'), False)
TRY_AGAIN_BTN = is_enabled(environ.get('TRY_AGAIN_BTN', 'True'), False)
auth_channel = environ.get('AUTH_CHANNEL', '-1003062493614')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

# Autres canaux
reqst_channel = environ.get('REQST_CHANNEL', '')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-1003095833778')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]

# MongoDB
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://elisabethboko45_db_user:kmrLKNKnfe8lK1df@cluster0.isv90ao.mongodb.net/?appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "jessikaSearch")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'jks_files')
MULTIPLE_DATABASE = is_enabled(environ.get('MULTIPLE_DATABASE', 'False'), False)
O_DB_URI = environ.get('O_DB_URI', "")
F_DB_URI = environ.get('F_DB_URI', "")
S_DB_URI = environ.get('S_DB_URI', "")

if not MULTIPLE_DATABASE:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = DATABASE_URI
    FILE_DB_URI = DATABASE_URI
    SEC_FILE_DB_URI = DATABASE_URI
else:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = O_DB_URI
    FILE_DB_URI = F_DB_URI
    SEC_FILE_DB_URI = S_DB_URI

# Mini App et URLs
MINI_APP_URL = environ.get('MINI_APP_URL', 'https://mayumixtg.vercel.app/')
MINI_APP_TUTORIAL_URL = environ.get('MINI_APP_TUTORIAL_URL', 'https://t.me/ZFlixTeam/3')

# Liens
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/+oEaqvXJYSnAwZTU0')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/ZFlixTeam')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'itz_kingcey')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/kingcey')

# Options
AI_SPELL_CHECK = is_enabled(environ.get('AI_SPELL_CHECK', 'True'), True)
PM_SEARCH = is_enabled(environ.get('PM_SEARCH', 'False'), False)
BUTTON_MODE = is_enabled(environ.get('BUTTON_MODE', 'True'), True)
MAX_BTN = is_enabled(environ.get('MAX_BTN', 'True'), True)
IMDB = is_enabled(environ.get('IMDB', 'True'), True)
AUTO_FFILTER = is_enabled(environ.get('AUTO_FFILTER', 'True'), True)
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE', 'True'), False)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get('LONG_IMDB_DESCRIPTION', 'False'), False)
SPELL_CHECK_REPLY = is_enabled(environ.get('SPELL_CHECK_REPLY', 'True'), True)
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', 'True'), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', 'False'), False)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', 'False'), False)
NO_RESULTS_MSG = is_enabled(environ.get('NO_RESULTS_MSG', 'False'), False)
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', 'True'), True)

# Streaming
STREAM_MODE = is_enabled(environ.get('STREAM_MODE', 'True'), True)
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get('PING_INTERVAL', '1200'))
ON_HEROKU = 'DYNO' in environ
URL = environ.get("URL", "https://mayuribot.koyeb.app/")

# Rename
RENAME_MODE = is_enabled(environ.get('RENAME_MODE', 'False'), False)

# Auto Approve
AUTO_APPROVE_MODE = is_enabled(environ.get('AUTO_APPROVE_MODE', 'False'), False)

# Misc
CACHE_TIME = int(environ.get('CACHE_TIME', 1800))
MAX_B_TN = environ.get("MAX_B_TN", "10")
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'JessiKa Search')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)

LANGUAGES = ["fr", "vf", "vostfr", "vo", "francais", "vost", "en", "english"]
SEASONS = ["saison 1", "saison 2", "saison 3", "saison 4", "saison 5",
           "saison 6", "saison 7", "saison 8", "saison 9", "saison 10"]
EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10",
            "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20",
            "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = [str(y) for y in range(1990, 2026)]

REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱",
             "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎",
             "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"]
