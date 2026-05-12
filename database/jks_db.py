# database/jks_db.py
import datetime
from database.users_chats_db import db

PLAN_DURATIONS = {
    "bronze":     7,
    "argent":     30,
    "or":         60,
    "platine":    90,
    "diamant":    180,
    "adamantide": 365,
}

PLAN_LABELS = {
    "bronze":     "Bronze — 7 jours",
    "argent":     "Argent — 30 jours",
    "or":         "Or — 60 jours",
    "platine":    "Platine — 90 jours",
    "diamant":    "Diamant — 180 jours",
    "adamantide": "Adamantide — 365 jours",
}

PLAN_PRICES = {
    "bronze":     {"fcfa": 520,    "cdf": 2500,   "usd": 0.94,  "stars": 50},
    "argent":     {"fcfa": 2100,   "cdf": 8800,   "usd": 3.80,  "stars": 200},
    "or":         {"fcfa": 4200,   "cdf": 17600,  "usd": 7.50,  "stars": 400},
    "platine":    {"fcfa": 6300,   "cdf": 26400,  "usd": 11.00, "stars": 600},
    "diamant":    {"fcfa": 12600,  "cdf": 52800,  "usd": 22.00, "stars": 1200},
    "adamantide": {"fcfa": 25200,  "cdf": 105500, "usd": 45.20, "stars": 2500},
}

FREE_SESSION_HOURS = 1


async def get_user_access(user_id: int) -> dict:
    """
    Retourne l'etat d'acces d'un utilisateur.
    Verifie d'abord le plan premium, ensuite la session gratuite.
    """
    user = await db.col.find_one({"id": int(user_id)})
    now = datetime.datetime.utcnow()

    result = {
        "has_access": False,
        "access_type": "none",
        "plan": "free",
        "session_expiry": None,
        "premium_expiry": None,
    }

    if not user:
        return result

    premium_expiry = user.get("premium_expiry")
    premium_plan = user.get("premium_plan")

    if premium_expiry and isinstance(premium_expiry, datetime.datetime):
        if premium_expiry > now:
            result.update({
                "has_access": True,
                "access_type": "premium",
                "plan": premium_plan or "free",
                "premium_expiry": premium_expiry,
            })
            return result
        else:
            await db.col.update_one(
                {"id": int(user_id)},
                {"$set": {"premium_plan": None, "premium_expiry": None}}
            )

    session_expiry = user.get("session_expiry")

    if session_expiry and isinstance(session_expiry, datetime.datetime):
        if session_expiry > now:
            result.update({
                "has_access": True,
                "access_type": "session",
                "plan": "free",
                "session_expiry": session_expiry,
            })
            return result

    return result


async def grant_free_session(user_id: int) -> datetime.datetime:
    """Attribue une session gratuite de 1 heure apres pub vue."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=FREE_SESSION_HOURS)
    await db.col.update_one(
        {"id": int(user_id)},
        {"$set": {"session_expiry": expiry}},
        upsert=True
    )
    return expiry


async def grant_premium_plan(user_id: int, plan: str) -> datetime.datetime:
    """Attribue un plan premium."""
    if plan not in PLAN_DURATIONS:
        raise ValueError(f"Plan inconnu : {plan}")
    days = PLAN_DURATIONS[plan]
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    await db.col.update_one(
        {"id": int(user_id)},
        {"$set": {
            "premium_plan": plan,
            "premium_expiry": expiry,
            "session_expiry": None,
        }},
        upsert=True
    )
    return expiry


async def revoke_premium(user_id: int) -> None:
    """Retire le plan premium d'un utilisateur."""
    await db.col.update_one(
        {"id": int(user_id)},
        {"$set": {"premium_plan": None, "premium_expiry": None}}
    )


async def get_all_premium_users() -> list:
    """Retourne tous les utilisateurs avec un plan premium actif."""
    now = datetime.datetime.utcnow()
    cursor = db.col.find({
        "premium_expiry": {"$gt": now},
        "premium_plan": {"$ne": None}
    })
    users = []
    async for user in cursor:
        users.append(user)
    return users


async def log_search(user_id: int, query: str) -> None:
    """Enregistre une recherche dans la collection search_history."""
    await db.db.search_history.insert_one({
        "user_id": int(user_id),
        "query": query.strip(),
        "timestamp": datetime.datetime.utcnow(),
    })


async def get_recent_searches(user_id: int, limit: int = 10) -> list:
    """Retourne les N dernieres recherches d'un utilisateur."""
    cursor = db.db.search_history.find(
        {"user_id": int(user_id)},
        {"_id": 0, "query": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        results.append(doc)
    return results


async def get_search_stats(user_id: int) -> dict:
    """Retourne les statistiques de recherche pour la Mini App."""
    now = datetime.datetime.utcnow()
    week_start = (now - datetime.timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    total = await db.db.search_history.count_documents({"user_id": int(user_id)})
    week_count = await db.db.search_history.count_documents({
        "user_id": int(user_id),
        "timestamp": {"$gte": week_start}
    })
    daily = []
    for i in range(7):
        day_start = week_start + datetime.timedelta(days=i)
        day_end = day_start + datetime.timedelta(days=1)
        count = await db.db.search_history.count_documents({
            "user_id": int(user_id),
            "timestamp": {"$gte": day_start, "$lt": day_end}
        })
        daily.append(count)
    return {
        "total_searches": total,
        "week_searches": week_count,
        "daily_searches": daily,
    }


def format_expiry(expiry: datetime.datetime) -> str:
    if not expiry:
        return "N/A"
    return expiry.strftime("%d %b %Y a %H:%M UTC")


def time_remaining(expiry: datetime.datetime) -> str:
    if not expiry:
        return "—"
    now = datetime.datetime.utcnow()
    delta = expiry - now
    if delta.total_seconds() <= 0:
        return "Expiree"
    total_seconds = int(delta.total_seconds())
    days    = total_seconds // 86400
    hours   = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if days > 0:
        return f"{days}j {hours}h {minutes}min"
    elif hours > 0:
        return f"{hours}h {minutes}min"
    elif minutes > 0:
        return f"{minutes}min {seconds}s"
    else:
        return f"{seconds}s"
