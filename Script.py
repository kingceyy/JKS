class script(object):

    START_TXT = """<blockquote>Hey {} ! 👋</blockquote>

<b>Mayumi</b> à votre service — je déniche vos films et séries en un clin d'œil.

Tapez un titre dans le groupe, et je vous trouve les fichiers disponibles.

<blockquote expandable><b>Accès :</b> regardez une pub sur la Mini App → <b>1h gratuite</b>, ou passez en <b>Premium</b> pour un accès illimité, sans limites.</blockquote>"""

    HELP_TXT = """<b>Aide — Mayumi</b>

Bonjour {} ! Voici les fonctionnalites disponibles."""

    ABOUT_TXT = """<blockquote>Informations sur le bot</blockquote>

<b>Nom :</b> <a href="https://t.me/{}">{}</a>
<b>Developpeur :</b> <a href="{}">Kingcey</a>
<b>Bibliotheque :</b> <a href="https://docs.pyrogram.org/">Pyrogram</a>
<b>Langage :</b> <a href="https://www.python.org/">Python 3</a>
<b>Base de donnees :</b> <a href="https://www.mongodb.com/">MongoDB</a>
<b>Version :</b> <code>1.0.0</code>"""

    MANUELFILTER_TXT = """<b>Aide — Filtres manuels</b>

Les filtres permettent de configurer des reponses automatiques pour des mots-cles specifiques.

<b>Remarques :</b>
- Le bot doit avoir les droits d'administrateur.
- Seuls les administrateurs peuvent ajouter des filtres dans un groupe.
- Les boutons d'alerte sont limites a 64 caracteres.

<b>Commandes disponibles :</b>
• /filter — <code>Ajouter un filtre dans un groupe</code>
• /filters — <code>Voir tous les filtres d'un groupe</code>
• /del — <code>Supprimer un filtre specifique</code>
• /delall — <code>Supprimer tous les filtres d'un groupe (proprietaire uniquement)</code>"""

    BUTTON_TXT = """<b>Aide — Boutons</b>

Ce bot supporte les boutons URL et les boutons d'alerte inline.

<b>Remarques :</b>
- Telegram n'autorise pas les boutons sans contenu — le contenu est obligatoire.
- Ce bot supporte les boutons avec tous les types de medias Telegram.
- Les boutons doivent etre correctement formates en Markdown.

<b>Boutons URL :</b>
<code>[Texte du bouton](buttonurl:https://t.me/ZFlixTeam)</code>

<b>Boutons d'alerte :</b>
<code>[Texte du bouton](buttonalert:Ceci est un message d'alerte)</code>"""

    AUTOFILTER_TXT = """<b>Aide — Filtre automatique</b>

<b>Indexation des fichiers :</b>
1. Ajoutez-moi comme administrateur de votre canal si celui-ci est prive.
2. Assurez-vous que votre canal ne contient pas de fichiers frauduleux ou de contenu interdit.
3. Transferez le dernier message avec citation. J'ajouterai tous les fichiers du canal a ma base de donnees.

<b>Utilisation du filtre automatique :</b>
1. Ajoutez le bot comme administrateur de votre groupe.
2. Utilisez /connect pour connecter votre groupe au bot.
3. Utilisez /settings en message prive et activez le filtre automatique dans le menu des parametres."""

    CONNECTION_TXT = """<b>Aide — Connexions</b>

Permet de connecter le bot en message prive pour gerer les filtres sans spammer le groupe.

<b>Remarques :</b>
- Seuls les administrateurs peuvent ajouter une connexion.
- Envoyez <code>/connect</code> pour connecter le bot a votre message prive.

<b>Commandes disponibles :</b>
• /connect — <code>Connecter un groupe a votre MP</code>
• /disconnect — <code>Se deconnecter d'un groupe</code>
• /connections — <code>Voir toutes vos connexions actives</code>"""

    EXTRAMOD_TXT = """<b>Aide — Modules supplementaires</b>

<b>Mainteneur :</b> <a href="{}">Proprietaire</a>
<b>Canal de mise a jour :</b> <a href="{}">Mayumi</a>

<b>Commandes disponibles :</b>
• /id — <code>Obtenir l'ID d'un utilisateur specifique</code>
• /info — <code>Obtenir les informations d'un utilisateur</code>
• /song — <code>Telecharger une chanson (exemple : /song nom de la chanson)</code>
• /telegraph — <code>Generer un lien Telegraph pour une photo ou video sous 5 Mo</code>
• /tts — <code>Convertir du texte en audio</code>
• /video — <code>Telecharger une video YouTube (exemple : /video https://youtu.be/...)</code>
• /font — <code>Generateur de polices stylisees (exemple : /font bonjour)</code>"""

    ADMIN_TXT = """<b>Aide — Commandes administrateur</b>

Ces commandes sont reservees aux administrateurs du bot.

<b>Commandes disponibles :</b>
• /logs — <code>Obtenir les erreurs recentes du bot</code>
• /stats — <code>Voir les statistiques des fichiers en base de donnees</code>
• /delete — <code>Supprimer un fichier specifique de la base de donnees</code>
• /users — <code>Voir la liste des utilisateurs et leurs IDs</code>
• /chats — <code>Voir la liste des groupes connectes</code>
• /leave — <code>Quitter un groupe</code>
• /disable — <code>Desactiver un groupe</code>
• /ban — <code>Bannir un utilisateur</code>
• /unban — <code>Debannir un utilisateur</code>
• /channel — <code>Voir la liste des canaux connectes</code>
• /broadcast — <code>Envoyer un message a tous les utilisateurs</code>
• /grp_broadcast — <code>Envoyer un message a tous les groupes connectes</code>
• /gfilter — <code>Ajouter un filtre global</code>
• /gfilters — <code>Voir tous les filtres globaux</code>
• /delg — <code>Supprimer un filtre global specifique</code>
• /delallg — <code>Supprimer tous les filtres globaux de la base de donnees</code>
• /deletefiles — <code>Supprimer les fichiers CamRip et PreDVD de la base de donnees</code>
• /request — <code>Envoyer une demande de film ou serie aux administrateurs</code>"""

    SEC_STATUS_TXT = """<b>Statistiques de la base de donnees</b>

<b>Utilisateurs totaux :</b> <code>{}</code>
<b>Groupes totaux :</b> <code>{}</code>
<b>Fichiers totaux :</b> <code>{}</code>
<b>Stockage utilise :</b> <code>{} Mo</code>
<b>Stockage libre :</b> <code>{} Mo</code>"""

    STATUS_TXT = """<b>Fichiers totaux (toutes bases) :</b> <code>{}</code>

<b>Base utilisateurs :</b>
<b>Utilisateurs :</b> <code>{}</code>
<b>Groupes :</b> <code>{}</code>

<b>Base de fichiers principale :</b>
<b>Fichiers :</b> <code>{}</code>
<b>Stockage utilise :</b> <code>{} Mo</code>
<b>Stockage libre :</b> <code>{} Mo</code>

<b>Base de fichiers secondaire :</b>
<b>Fichiers :</b> <code>{}</code>
<b>Stockage utilise :</b> <code>{} Mo</code>
<b>Stockage libre :</b> <code>{} Mo</code>

<b>Autre base :</b>
<b>Stockage utilise :</b> <code>{} Mo</code>
<b>Stockage libre :</b> <code>{} Mo</code>"""

    LOG_TEXT_G = """<b>#NouveauGroupe</b>
<b>Groupe :</b> {} (<code>{}</code>)
<b>Membres :</b> <code>{}</code>
<b>Ajoute par :</b> {}"""

    LOG_TEXT_P = """<b>#NouvelUtilisateur</b>
<b>ID :</b> <code>{}</code>
<b>Nom :</b> {}"""

    ALRT_TXT = """Bonjour {},

Ce fichier a ete demande par quelqu'un d'autre. Veuillez faire votre propre demande."""

    OLD_ALRT_TXT = """Bonjour {},

Vous utilisez un ancien message du bot. Veuillez faire une nouvelle demande."""

    CUDNT_FND = """Aucun resultat trouve pour <b>{}</b>.

Vouliez-vous dire l'un de ces titres ?"""

    I_CUDNT = """<b>Aucun fichier trouve pour votre demande : {}</b>

Verifiez l'orthographe sur Google et reessayez.

<b>Format pour un film :</b>
<i>Exemple : Inception ou Inception 2010</i>

<b>Format pour une serie :</b>
<i>Exemple : Loki S01 ou Loki S01E04</i>

Evitez les caracteres speciaux : <code>: ! , . / ) (</code>"""

    I_CUD_NT = """Aucun fichier trouve pour <b>{}</b>.

Verifiez l'orthographe sur Google ou IMDb."""

    MVE_NT_FND = """Ce titre n'est pas disponible dans la base de donnees."""

    TOP_ALRT_MSG = """Recherche en cours dans la base de donnees..."""

    MELCOW_ENG = """<b>Bienvenue {} dans le groupe {} ! 🎉</b>"""

    REQINFO = """<blockquote>Information importante</blockquote>

Ce message sera automatiquement supprime dans <b>5 minutes</b>.

Si vous ne voyez pas le fichier demande, consultez la page suivante."""

    SELECT = """Selectionnez votre langue, qualite, saison et episode preferes."""

    NORSLTS = """<b>#AucunResultat</b>

<b>ID :</b> {}
<b>Nom :</b> {}
<b>Message :</b> {}"""

    CAPTION = """<b>Nom du fichier :</b> {file_name}

<b>Taille :</b> {file_size}"""

    IMDB_TEMPLATE_TXT = """<b>Titre :</b> <a href={url}>{title}</a>
<b>Genres :</b> {genres}
<b>Annee :</b> <a href={url}/releaseinfo>{year}</a>
<b>Note :</b> <a href={url}/ratings>{rating}</a> / 10 (base sur {votes} evaluations)
<b>Langues :</b> <code>{languages}</code>
<b>Duree :</b> {runtime} minutes
<b>Date de sortie :</b> {release_date}
<b>Pays :</b> <code>{countries}</code>

<i>Resultat affiche en {remaining_seconds} secondes — Demande par {user_mention}</i>"""

    ALL_FILTERS = """<b>Bonjour {}, voici les trois types de filtres disponibles.</b>"""

    GFILTER_TXT = """<b>Bienvenue dans les filtres globaux.</b>

Les filtres globaux sont definis par les administrateurs du bot et s'appliquent a tous les groupes connectes.

<b>Commandes disponibles :</b>
• /gfilter — <code>Creer un filtre global</code>
• /gfilters — <code>Voir tous les filtres globaux</code>
• /delg — <code>Supprimer un filtre global specifique</code>
• /delallg — <code>Supprimer tous les filtres globaux</code>"""

    FILE_STORE_TXT = """<b>File Store</b> permet de creer un lien partageable pour un ou plusieurs fichiers.

<b>Commandes disponibles :</b>
• /batch — <code>Creer un lien batch pour plusieurs fichiers</code>
• /link — <code>Creer un lien pour un seul fichier</code>
• /pbatch — <code>Identique a /batch, mais les fichiers sont proteges contre le transfert</code>
• /plink — <code>Identique a /link, mais le fichier est protege contre le transfert</code>"""

    SONG_TXT = """<b>Module de telechargement de musique</b>

Telechargez n'importe quelle chanson avec une vitesse elevee.

<b>Utilisation :</b> /song nom de la chanson
<i>Exemple : /song Shape of You</i>"""

    YTDL_TXT = """<b>Module de telechargement YouTube</b>

Telechargez n'importe quelle video depuis YouTube.

<b>Utilisation :</b> /video lien_youtube
<i>Exemple : /video https://youtu.be/exemple</i>"""

    TTS_TXT = """<b>Module de synthese vocale (TTS)</b>

Convertit du texte en audio.

<b>Utilisation :</b> /tts votre texte"""

    GTRANS_TXT = """<b>Module de traduction Google</b>

Traduit un texte dans la langue de votre choix.

<b>Utilisation :</b> /tr code_langue votre texte

<b>Codes de langue :</b>
• <code>fr</code> — Francais
• <code>en</code> — Anglais
• <code>es</code> — Espagnol
• <code>de</code> — Allemand"""

    TELE_TXT = """<b>Module Telegraph</b>

Genere un lien Telegraph pour une photo ou une video (sous 5 Mo).

<b>Utilisation :</b> /telegraph — Envoyez-moi une photo ou une video."""

    PROGRESS_BAR = """\n
Renommage en cours...
Fichier : {1} | {2}
Progression : {0}%
Vitesse : {3}/s
Temps restant : {4}"""

    PINGS_TXT = """<b>Module de ping</b>

<b>Commandes :</b>
• /alive — Verifier si le bot est en ligne
• /help — Obtenir de l'aide
• /ping — Obtenir votre ping"""

    STICKER_TXT = """<b>Module Sticker</b>

Permet d'obtenir l'ID d'un sticker.

<b>Utilisation :</b> /stickerid — Repondez a un sticker"""

    FONT_TXT = """<b>Module de polices</b>

Genere du texte dans des styles de polices varies.

<b>Utilisation :</b> /font votre texte
<i>Exemple : /font Bonjour</i>"""

    PURGE_TXT = """<b>Module de suppression en masse</b>

Supprime un grand nombre de messages dans un groupe.

<b>Commandes :</b>
• /purge — Supprimer tous les messages depuis le message cite jusqu'au message actuel"""

    WHOIS_TXT = """<b>Module d'informations utilisateur</b>

<b>Commandes :</b>
• /whois — Obtenir les informations completes d'un utilisateur"""

    JSON_TXT = """<b>Module JSON</b>

Retourne le JSON de n'importe quel message en reponse avec /json.

Disponible en message prive et en groupe."""

    URLSHORT_TXT = """<b>Module de raccourcissement d'URL</b>

<b>Utilisation :</b> /short lien_a_raccourcir
<i>Exemple : /short https://youtu.be/exemple</i>"""

    GEN_PASS = """<b>Module de generation de mot de passe</b>

Genere un mot de passe aleatoire selon la longueur specifiee.

<b>Utilisation :</b> /genpassword longueur
<i>Exemple : /genpassword 20</i>

<b>Remarques :</b>
• Seuls les chiffres sont autorises comme parametre
• Longueur maximale : 84 caracteres"""

    SHARE_TXT = """<b>Partage de texte</b>

Genere une URL partageable pour votre texte.

<b>Utilisation :</b> /share votre texte"""

    PIN_TXT = """<b>Module d'epinglage de messages</b>

<b>Commandes :</b>
• /pin — Epingler un message dans le groupe
• /unpin — Desepingler le message actuel"""

    RESTART_TXT = """<b>Bot redemarre avec succes !</b>

<b>Date :</b> <code>{}</code>
<b>Heure :</b> <code>{}</code>
<b>Fuseau horaire :</b> <code>UTC</code>
<b>Version :</b> <code>1.0.0</code>"""

    RENAME_TXT = """<b>Module de renommage de fichiers</b>

<u>Definir une miniature personnalisee :</u>
• /set_thumb — Envoyez une photo pour definir la miniature automatiquement
• /del_thumb — Supprimer votre miniature actuelle
• /view_thumb — Afficher votre miniature actuelle

<u>Definir une legende personnalisee :</u>
• /set_caption — Definir une legende personnalisee
• /see_caption — Voir votre legende actuelle
• /del_caption — Supprimer votre legende

<i>Exemple : /set_caption Nom : {filename} — Taille : {filesize}</i>

<u>Renommer un fichier :</u>
• /rename — Repondez a un fichier avec cette commande, puis saisissez le nouveau nom"""

    STREAM_TXT = """<b>Lien de streaming et de telechargement</b>

<b>Utilisation :</b> /stream — Obtenez un lien streamable et telechargeable pour n'importe quel fichier"""

    ABOOK_TXT = """<b>Module Audiobook</b>

Convertit un fichier PDF en fichier audio.

<b>Utilisation :</b> /audiobook — Repondez a un fichier PDF avec cette commande"""

    CARB_TXT = """<b>Module Carbon</b>

Genere une image stylisee a partir de votre texte.

<b>Utilisation :</b> /carbon — Repondez a un texte avec cette commande"""

    # Logs channel
    # Info shortlink (conservé pour compatibilité avec commands.py)
    SINFO = """Aucune information disponible."""

    CLONE_TXT = """Le mode clone a été désactivé."""

    ENGLISH_INFO = """Information non disponible."""
    HINDI_INFO = """Information non disponible."""
    TAMIL_INFO = """Information non disponible."""
    TELUGU_INFO = """Information non disponible."""
    MALAYALAM_INFO = """Information non disponible."""
    KANNADA_INFO = """Information non disponible."""
    GUJARATI_INFO = """Information non disponible."""
    URDU_INFO = """Information non disponible."""
    BANGLADESH_INFO = """Information non disponible."""

    LOGO = """
   ╔══════════════════════════════════════╗
   ║         Mayumi Bot           ║
   ║      Développé par @kingcey          ║
   ║   Canal : t.me/ZFlixTeam         ║
   ╚══════════════════════════════════════╝
"""
