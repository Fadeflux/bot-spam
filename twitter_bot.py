"""
=============================================================
  AUTOMATISATION DE COMMENTAIRES - Twitter/X API v2
  Authentification OAuth 1.0a (PIN-based) via Tweepy
=============================================================

PRÉREQUIS :
    pip install tweepy python-dotenv

CONFIGURATION :
    Créer un fichier .env avec vos clés API Developer :

        API_KEY=xxxxxxxxxxxxxxxxxxxx
        API_SECRET=xxxxxxxxxxxxxxxxxxxx

    Les Access Token sont générés automatiquement via OAuth
    au premier lancement et sauvegardés dans .env.
"""

import tweepy
import time
import re
import logging
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv, set_key

# ──────────────────────────────────────────────
# 1. CONFIGURATION - Chargement des clés API
# ──────────────────────────────────────────────

ENV_FILE = ".env"
load_dotenv(ENV_FILE)

# Pour un compte unique (rétro-compatibilité)
API_KEY             = os.getenv("API_KEY")
API_SECRET          = os.getenv("API_SECRET")
ACCESS_TOKEN        = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN        = os.getenv("BEARER_TOKEN")


# ──────────────────────────────────────────────
# SUPPORT MULTIPLE COMPTES
# ──────────────────────────────────────────────

def charger_tous_comptes():
    """
    Charge TOUS les comptes disponibles depuis .env.
    
    Format attendu dans .env :
        # Compte 1
        ACCOUNT1_API_KEY=xxx
        ACCOUNT1_API_SECRET=xxx
        ACCOUNT1_ACCESS_TOKEN=xxx
        ACCOUNT1_ACCESS_TOKEN_SECRET=xxx
        ACCOUNT1_BEARER_TOKEN=xxx
        
        # Compte 2
        ACCOUNT2_API_KEY=xxx
        ACCOUNT2_API_SECRET=xxx
        ...
    
    Returns:
        Dictionnaire {numero_compte: {cles_auth}}
    """
    comptes = {}
    i = 1
    while True:
        api_key = os.getenv(f"ACCOUNT{i}_API_KEY")
        if not api_key:
            break
        comptes[i] = {
            "api_key": api_key,
            "api_secret": os.getenv(f"ACCOUNT{i}_API_SECRET"),
            "access_token": os.getenv(f"ACCOUNT{i}_ACCESS_TOKEN"),
            "access_token_secret": os.getenv(f"ACCOUNT{i}_ACCESS_TOKEN_SECRET"),
            "bearer_token": os.getenv(f"ACCOUNT{i}_BEARER_TOKEN"),
        }
        i += 1
    return comptes


# ──────────────────────────────────────────────
# 2. AUTHENTIFICATION OAUTH 1.0A (PIN-based)
# ──────────────────────────────────────────────

# Cache temporaire pour les sessions OAuth
# Chaque session contient des données + un timestamp pour le timeout
_oauth_sessions = {}
_OAUTH_SESSION_TIMEOUT = 1800  # 30 minutes en secondes
import time

def _nettoyer_sessions_expirees():
    """Supprime les sessions OAuth expirées (> 30 min)."""
    now = time.time()
    sessions_expirees = [
        sid for sid, data in _oauth_sessions.items()
        if now - data.get("created_at", 0) > _OAUTH_SESSION_TIMEOUT
    ]
    for sid in sessions_expirees:
        del _oauth_sessions[sid]
        print(f"⏰ Session OAuth {sid[:8]}... expirée (> 30 min)")

def generer_url_oauth(numero_compte=None):
    """
    Génère l'URL OAuth pour autoriser un compte.
    
    Returns:
        (auth_url, session_id) : URL à ouvrir + identifiant session
    """
    # Nettoie les sessions expirées avant de créer une nouvelle
    _nettoyer_sessions_expirees()
    
    # OAuth DOIT TOUJOURS utiliser les clés du compte développeur
    # Le compte normal sera rempli avec les tokens d'accès obtenus
    api_key = API_KEY
    api_secret = API_SECRET
    
    if numero_compte:
        prefix = f"ACCOUNT{numero_compte}_"
    else:
        prefix = ""
    
    if not api_key or not api_secret:
        raise ValueError("API_KEY ou API_SECRET manquants (clés du compte développeur)")
    
    oauth_handler = tweepy.OAuth1UserHandler(
        consumer_key=api_key,
        consumer_secret=api_secret,
        callback="oob"
    )
    
    auth_url = oauth_handler.get_authorization_url()
    
    # Stocke la session pour la valider plus tard
    import uuid
    session_id = str(uuid.uuid4())
    _oauth_sessions[session_id] = {
        "oauth_handler": oauth_handler,
        "numero_compte": numero_compte,
        "prefix": prefix,
        "api_key": api_key,
        "api_secret": api_secret,
        "bearer_token": os.getenv(f"{prefix}BEARER_TOKEN") if prefix else BEARER_TOKEN,
        "created_at": time.time()  # Timestamp pour tracker l'expiration
    }
    
    return auth_url, session_id


def valider_pin_oauth(session_id, pin):
    """
    Valide le PIN et retourne les tokens d'accès.
    
    Args:
        session_id : ID retourné par generer_url_oauth
        pin        : PIN fourni par l'utilisateur
    
    Returns:
        (access_token, access_token_secret, username, message)
    """
    # Nettoie les sessions expirées avant de valider
    _nettoyer_sessions_expirees()
    
    if session_id not in _oauth_sessions:
        raise ValueError(
            "❌ Session OAuth expirée ou invalide.\n\n"
            "Raisons possibles:\n"
            "  • Le PIN a expiré (valide 30 min)\n"
            "  • Vous avez rouvert la page OAuth\n"
            "  • Le serveur a redémarré\n\n"
            "Solution: Cliquez sur 'Recommencer' pour créer une nouvelle session."
        )
    
    session = _oauth_sessions[session_id]
    
    if not re.fullmatch(r"\d{7}", pin):
        raise ValueError("PIN invalide (doit être 7 chiffres)")
    
    try:
        access_token, access_token_secret = session["oauth_handler"].get_access_token(pin)
    except tweepy.TweepyException as e:
        raise ValueError(f"PIN incorrect ou expiré: {str(e)}")
    
    # Sauvegarde les tokens dans .env
    prefix = session["prefix"]
    set_key(ENV_FILE, f"{prefix}API_KEY", session["api_key"])
    set_key(ENV_FILE, f"{prefix}API_SECRET", session["api_secret"])
    set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN", access_token)
    set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN_SECRET", access_token_secret)
    set_key(ENV_FILE, f"{prefix}BEARER_TOKEN", session.get("bearer_token") or "")
    
    # Recharge .env globalement
    load_dotenv(ENV_FILE, override=True)
    
    # Récupère l'username
    try:
        client = tweepy.Client(
            bearer_token=session.get("bearer_token"),
            consumer_key=session["api_key"],
            consumer_secret=session["api_secret"],
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        me = client.get_me()
        username = me.data.username
        name = me.data.name
    except Exception as e:
        username = "inconnu"
        name = "Compte"
    
    # Supprime la session
    del _oauth_sessions[session_id]
    
    return access_token, access_token_secret, username, f"Compte {name} (@{username}) authentifié avec succès !"


def connecter_compte(numero_compte=None):
    """
    Connecte un compte Twitter via OAuth 1.0a avec flow PIN.

    Args:
        numero_compte : Si spécifié, charge le compte ACCOUNT[numero].
                       Si None, charge depuis API_KEY/API_SECRET (rétro-compat).

    - Si les Access Token sont déjà dans .env → connexion directe.
    - Sinon → ouvre l'URL d'autorisation Twitter dans le terminal,
      demande le PIN, génère les tokens et les sauvegarde dans .env.

    Returns:
        (client, username) : client Tweepy authentifié + @username du compte
    """
    global ACCESS_TOKEN, ACCESS_TOKEN_SECRET

    if numero_compte:
        # Chargement depuis ACCOUNT[numero]
        api_key = os.getenv(f"ACCOUNT{numero_compte}_API_KEY")
        api_secret = os.getenv(f"ACCOUNT{numero_compte}_API_SECRET")
        access_token = os.getenv(f"ACCOUNT{numero_compte}_ACCESS_TOKEN")
        access_token_secret = os.getenv(f"ACCOUNT{numero_compte}_ACCESS_TOKEN_SECRET")
        bearer_token = os.getenv(f"ACCOUNT{numero_compte}_BEARER_TOKEN")
        prefix = f"ACCOUNT{numero_compte}_"
    else:
        # Rétro-compatibilité : comptes uniques
        api_key = API_KEY
        api_secret = API_SECRET
        access_token = ACCESS_TOKEN
        access_token_secret = ACCESS_TOKEN_SECRET
        bearer_token = BEARER_TOKEN
        prefix = ""

    print("\n" + "=" * 55)
    if numero_compte:
        print(f"  🔐 CONNEXION AU COMPTE {numero_compte}")
    else:
        print("  🔐 CONNEXION AU COMPTE TWITTER")
    print("=" * 55)

    if not api_key or not api_secret:
        print("\n  ❌ API_KEY et API_SECRET manquants dans .env")
        print("     Créez un fichier .env avec vos clés Developer.")
        sys.exit(1)

    # Si Access Token déjà présents → pas besoin du flow PIN
    if access_token and access_token_secret:
        print("\n  ✅ Access Token trouvés dans .env → connexion directe")
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        try:
            me = client.get_me()
            username = me.data.username
            name     = me.data.name
            print(f"  👤 Compte connecté : {name} (@{username})")
            return client, username
        except tweepy.TweepyException as e:
            print(f"  ❌ Token invalide ou expiré : {e}")
            print("     Supprimez les tokens de .env et relancez.")
            sys.exit(1)

    # ── Flow PIN OAuth 1.0a ──
    print("\n  Aucun Access Token trouvé → lancement du flow OAuth\n")

    oauth_handler = tweepy.OAuth1UserHandler(
        consumer_key=api_key,
        consumer_secret=api_secret,
        callback="oob"   # "oob" = Out-Of-Band = mode PIN
    )

    try:
        auth_url = oauth_handler.get_authorization_url()
    except tweepy.TweepyException as e:
        print(f"  ❌ Impossible de générer l'URL OAuth : {e}")
        sys.exit(1)

    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  Ouvrez ce lien dans votre navigateur :         │")
    print("  │                                                  │")
    print(f"  │  {auth_url[:48]}  │")
    if len(auth_url) > 48:
        print(f"  │  {auth_url[48:96]}  │")
    print("  │                                                  │")
    print("  │  Connectez-vous au compte qui doit poster,      │")
    print("  │  puis copiez le PIN affiché par Twitter.        │")
    print("  └─────────────────────────────────────────────────┘")
    print(f"\n  URL complète : {auth_url}\n")

    # Saisie du PIN
    while True:
        pin = input("  Entrez le PIN Twitter (7 chiffres) : ").strip()
        if re.fullmatch(r"\d{7}", pin):
            break
        print("  ❌ PIN invalide, il doit contenir exactement 7 chiffres.")

    try:
        access_token, access_token_secret = oauth_handler.get_access_token(pin)
    except tweepy.TweepyException as e:
        print(f"\n  ❌ PIN incorrect ou expiré : {e}")
        sys.exit(1)

    # Sauvegarde dans .env pour les prochains lancements
    set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN",        access_token)
    set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN_SECRET", access_token_secret)
    if numero_compte:
        set_key(ENV_FILE, f"{prefix}BEARER_TOKEN", bearer_token or "")
    ACCESS_TOKEN        = access_token
    ACCESS_TOKEN_SECRET = access_token_secret
    print("\n  ✅ Access Token sauvegardés dans .env")

    # Création du client authentifié
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
    )

    # Vérification du compte connecté
    try:
        me = client.get_me()
        username = me.data.username
        name     = me.data.name
        print(f"  👤 Compte connecté : {name} (@{username})")
    except tweepy.TweepyException as e:
        print(f"  ⚠️  Impossible de récupérer le profil : {e}")
        username = "inconnu"

    return client, username


# ──────────────────────────────────────────────
# 3. EXTRACTION DE L'ID DEPUIS UN LIEN TWITTER
# ──────────────────────────────────────────────

def extraire_id_depuis_lien(lien):
    """
    Extrait l'ID numérique d'un tweet à partir de son URL.

    Formats supportés :
        https://twitter.com/user/status/1234567890
        https://x.com/user/status/1234567890
        https://mobile.twitter.com/user/status/1234567890

    Returns:
        ID du tweet (str) ou None si lien invalide
    """
    pattern = r"(?:twitter\.com|x\.com)/\w+/status/(\d+)"
    match   = re.search(pattern, lien)

    if match:
        tweet_id = match.group(1)
        print(f"   🔗 ID extrait : {tweet_id}")
        return tweet_id
    else:
        print(f"   ❌ Lien invalide : {lien}")
        return None


# ──────────────────────────────────────────────
# 4. RÉCUPÉRATION DU TWEET
# ──────────────────────────────────────────────

def recuperer_tweet(client, tweet_id):
    """
    Récupère le contenu d'un tweet via son ID.

    Returns:
        Objet tweet ou None si introuvable
    """
    try:
        response = client.get_tweet(
            id=tweet_id,
            tweet_fields=["id", "text", "author_id", "created_at"]
        )
        if response.data:
            print(f"   ✅ Tweet récupéré : {response.data.text[:80]}...")
            return response.data
        else:
            print(f"   ⚠️  Tweet introuvable (ID: {tweet_id})")
            return None
    except tweepy.TweepyException as e:
        print(f"   ❌ Erreur API : {e}")
        return None


# ──────────────────────────────────────────────
# 5. GÉNÉRATION DES COMMENTAIRES
# ──────────────────────────────────────────────

def generer_commentaire(tweet_texte, modele="contextuel"):
    """
    Génère un commentaire personnalisé via combinaisons de segments.

    Args:
        tweet_texte : Texte du tweet ciblé
        modele      : "simple" (aléatoire) ou "contextuel" (adapté)

    Returns:
        Commentaire (str)
    """
    import random

    # Segments combinatoires
    debuts = [
        "Great",
        "Awesome",
        "Excellent",
        "Brilliant",
        "Fantastic",
        "Amazing",
        "Incredible"
    ]

    milieux = [
        "content",
        "resource",
        "article",
        "post",
        "perspective",
        "analysis",
        "approach"
    ]

    fins = [
        "thanks for sharing! 🙌",
        "love this 🔥",
        "well done! 👍",
        "super helpful 💡",
        "keep it up! 🚀",
        "mind-blowing! 🤩",
        "impressive! ⚡"
    ]

    # Combinaisons aleatoires
    combinaison = f"{random.choice(debuts)} {random.choice(milieux)}, {random.choice(fins)}"

    return combinaison


# ──────────────────────────────────────────────
# 6. POSTER UN COMMENTAIRE (REPLY)
# ──────────────────────────────────────────────

def poster_commentaire(client, tweet_id, commentaire, compte, simulation=True):
    """
    Poste un commentaire (reply) sur un tweet donné.

    Args:
        client      : Client Twitter authentifié
        tweet_id    : ID du tweet cible
        commentaire : Texte du commentaire
        compte      : @username du compte qui poste
        simulation  : Si True, simule sans vraiment poster

    Returns:
        ID du nouveau tweet posté, ou None en simulation
    """
    if simulation:
        print(f"   [SIMULATION] 💬 @{compte} → '{commentaire}'")
        return None

    try:
        response = client.create_tweet(
            text=commentaire,
            in_reply_to_tweet_id=tweet_id
        )
        nouveau_id = response.data["id"]
        print(f"   ✅ Commentaire posté par @{compte} (ID: {nouveau_id})")
        return nouveau_id
    except tweepy.TweepyException as e:
        print(f"   ❌ Erreur lors du post : {e}")
        return None


# ──────────────────────────────────────────────
# 7. PIPELINE PRINCIPAL
# ──────────────────────────────────────────────

def automatiser_depuis_liens(
    client,
    compte,
    liens,
    nb_commentaires=1,
    delai=10,
    simulation=True,
    simulation_locale=False
):
    """
    Pipeline complet : liens → extraction ID → récupération tweet
                       → génération commentaire(s) → publication.

    Args:
        client            : Client Tweepy authentifié
        compte            : @username du compte source
        liens             : Liste d'URLs de tweets
        nb_commentaires   : Nombre de commentaires par tweet
        delai             : Secondes entre chaque post
        simulation        : True = ne poste pas réellement
        simulation_locale : True = sans aucun appel API
    """
    print("\n" + "=" * 55)
    print("  🤖 AUTOMATISATION DE COMMENTAIRES - Twitter/X")
    print("=" * 55)
    print(f"  Compte       : @{compte}")
    if simulation_locale:
        print(f"  Mode         : 🟢 SIMULATION LOCALE (sans API)")
    else:
        print(f"  Mode         : {'🟡 SIMULATION' if simulation else '🔴 RÉEL'}")
    print(f"  Nb liens     : {len(liens)}")
    print(f"  Commentaires : {nb_commentaires} par tweet")
    print(f"  Délai        : {delai}s entre chaque post")
    print(f"  Total prévu  : {len(liens) * nb_commentaires} commentaire(s)")
    print("=" * 55)

    tweets_exemples = {
        "python": "Excellentes performances en Python avec async/await ! 🐍",
        "ia":     "L'IA continue de transformer nos workflows 🤖",
        "js":     "React 19 va changer la façon d'écrire du JavaScript 🚀",
        "default":"Très intéressant, merci pour le partage ! 👍"
    }

    resultats = []
    post_count = 0

    for i, lien in enumerate(liens, 1):
        print(f"\n📌 Post {i}/{len(liens)}")
        print(f"   Lien : {lien}")

        # Étape 1 : Extraire l'ID
        tweet_id = extraire_id_depuis_lien(lien)
        if not tweet_id:
            print("   ⏭️  Lien ignoré (invalide).")
            continue

        # Étape 2 : Récupérer le tweet
        if simulation_locale:
            mot = lien.split('/')[-3].lower() if '/' in lien else "default"
            tweet_texte = tweets_exemples.get(mot, tweets_exemples["default"])
            print(f"   ✅ Tweet simulé : {tweet_texte[:60]}...")
        else:
            tweet = recuperer_tweet(client, tweet_id)
            if not tweet:
                print("   ⏭️  Tweet ignoré (introuvable ou supprimé).")
                continue
            tweet_texte = tweet.text

        # Étape 3 : Poster nb_commentaires fois
        for j in range(1, nb_commentaires + 1):
            commentaire = generer_commentaire(tweet_texte, modele="contextuel")

            if nb_commentaires > 1:
                print(f"   💬 Commentaire {j}/{nb_commentaires}")

            if simulation_locale:
                print(f"   [SIM LOCAL] 💬 @{compte} → '{commentaire}'")
                nouveau_id = None
            else:
                nouveau_id = poster_commentaire(
                    client, tweet_id, commentaire,
                    compte=compte, simulation=simulation
                )

            resultats.append({
                "lien"        : lien,
                "tweet_id"    : tweet_id,
                "commentaire" : commentaire,
                "posted_id"   : nouveau_id,
                "compte"      : compte
            })
            post_count += 1

            # Délai entre les posts (sauf le dernier)
            if post_count < len(liens) * nb_commentaires:
                print(f"   ⏳ Attente de {delai} secondes...")
                if not simulation_locale:
                    time.sleep(delai)

    # ── Résumé final ──
    print("\n" + "=" * 55)
    print(f"  ✅ Terminé ! {len(resultats)}/{len(liens) * nb_commentaires} commentaire(s) traité(s)")
    print(f"  📤 Compte source : @{compte}")
    print("=" * 55)
    for r in resultats:
        statut = f"ID {r['posted_id']}" if r['posted_id'] else "simulé"
        print(f"  • {r['lien'][:48]}... → {statut}")

    return resultats


def lancer_comptes_parallelement(clients, liens, nb_commentaires=1, delai=10, simulation=True, simulation_locale=False):
    """
    Lance tous les comptes EN MÊME TEMPS (multithreading).
    
    Args:
        clients : Dict {numero: (client, username)}
        liens : Liste d'URLs
        ... (mêmes paramètres que automatiser_depuis_liens)
    
    Chaque compte poste ses commentaires dans son propre thread.
    """
    print("\n" + "=" * 70)
    print("  🚀 LANCEMENT PARALLÈLE - Tous les comptes COMMENTENT EN MÊME TEMPS !")
    print("=" * 70)
    print(f"\n  📊 Configuration :")
    print(f"     • Nombre de comptes      : {len(clients)}")
    print(f"     • Nombre de tweets       : {len(liens)}")
    print(f"     • Commentaires/tweet     : {nb_commentaires}")
    print(f"     • Délai entre posts      : {delai}s")
    print(f"     • Total de commentaires  : {len(clients) * len(liens) * nb_commentaires}")
    print("\n" + "=" * 70 + "\n")

    threads = []
    resultats_par_compte = {}
    lock = threading.Lock()  # Pour éviter les conflits d'affichage

    def executer_compte(compte_num, client, username):
        """Exécute la tâche pour un compte spécifique."""
        print(f"\n   🔵 [{username}] DÉMARRAGE → Poste des commentaires...")
        resultats = automatiser_depuis_liens(
            client=client,
            compte=username,
            liens=liens,
            nb_commentaires=nb_commentaires,
            delai=delai,
            simulation=simulation,
            simulation_locale=simulation_locale
        )
        with lock:
            resultats_par_compte[username] = resultats
        print(f"   ✅ [{username}] TERMINÉ → Tous les commentaires sont postés !")

    # Crée un thread par compte
    for compte_num in sorted(clients.keys()):
        client, username = clients[compte_num]
        
        thread = threading.Thread(
            target=executer_compte,
            args=(compte_num, client, username),
            name=f"Compte-{username}"
        )
        thread.daemon = False
        thread.start()
        threads.append(thread)

    # Attend que TOUS les threads se terminent
    print("   ⏳ Tous les comptes travaillent en parallèle...\n")
    for thread in threads:
        thread.join()

    # ── RÉSUMÉ FINAL ──
    print("\n" + "=" * 70)
    print("  ✅ RÉSUMÉ FINAL - TOUS LES COMPTES ONT TERMINÉ !")
    print("=" * 70)
    
    total_commentaires = 0
    for username, resultats in resultats_par_compte.items():
        nb = len(resultats)
        total_commentaires += nb
        statut = "✅" if nb > 0 else "⚠️"
        print(f"   {statut} @{username} → {nb} commentaire(s) traité(s)")
    
    print("\n" + "-" * 70)
    print(f"   📊 TOTAL : {total_commentaires} commentaire(s) postés par {len(clients)} compte(s)")
    print("=" * 70 + "\n")




# ──────────────────────────────────────────────
# 8. MENU DE BIENVENUE - CONNEXION DE COMPTE
# ──────────────────────────────────────────────

def menu_connexion():
    """
    Menu de bienvenue au démarrage du bot.
    Demande à l'utilisateur de se connecter ou d'ajouter un compte.
    """
    print("\n" + "=" * 70)
    print("  🐦 TWITTER BOT — Bienvenue !")
    print("=" * 70)
    print("\n  Voulez-vous vous connecter à un compte Twitter ? (O/N)")
    
    choix = input("\n  👉 Votre choix : ").strip().upper()
    
    if choix not in ["O", "Y", "OUI", "YES"]:
        print("\n  ❌ Connexion annulée. Au revoir ! 👋\n")
        return False
    
    # ── Vérifier les comptes existants ──
    comptes_dispo = charger_tous_comptes()
    
    while True:
        print("\n" + "=" * 70)
        print("  🔐 OPTIONS DE CONNEXION")
        print("=" * 70)
        
        if comptes_dispo:
            print(f"\n  📋 COMPTES EXISTANTS ({len(comptes_dispo)} compte(s)) :\n")
            for num in sorted(comptes_dispo.keys()):
                print(f"      {num}) Compte {num}")
            print("\n  " + "─" * 66)
        
        print("  OPTIONS :\n")
        if comptes_dispo:
            print(f"      C) 🔓 Se connecter avec un compte existant")
        print(f"      N) ➕ AJOUTER UN NOUVEAU COMPTE (via OAuth)")
        print(f"      Q) ❌ Quitter")
        print("\n" + "─" * 70)
        
        choix = input("\n  👉 Votre choix (C/N/Q) : ").strip().upper()
        
        if choix == "Q":
            print("\n  ❌ Annulé. Au revoir ! 👋\n")
            return False
        
        if choix == "N":
            print("\n" + "=" * 70)
            interface_ajouter_compte()
            print("=" * 70)
            load_dotenv(ENV_FILE, override=True)  # Recharge .env
            comptes_dispo = charger_tous_comptes()
            continue
        
        if choix == "C" and comptes_dispo:
            print("\n  📋 SÉLECTION DU COMPTE :\n")
            for num in sorted(comptes_dispo.keys()):
                print(f"      {num}) Compte {num}")
            
            while True:
                num_str = input("\n  👉 Numéro du compte : ").strip()
                try:
                    num = int(num_str)
                    if num in comptes_dispo:
                        print(f"\n  ✅ Tentative de connexion au compte {num}...\n")
                        client, username = connecter_compte(num)
                        print(f"\n  ✅ Connecté ! Bienvenue @{username} ! 👋\n")
                        return True
                    else:
                        print(f"  ❌ Numéro invalide.")
                except ValueError:
                    print(f"  ❌ Entrez un numéro valide.")
        else:
            print("\n  ❌ Choix invalide.")


# ──────────────────────────────────────────────
# 9. INTERFACE INTERACTIVE TERMINAL
# ──────────────────────────────────────────────

def interface_ajouter_compte():
    """
    Ajoute un nouveau compte à la configuration.
    Demande à l'utilisateur de se connecter via OAuth PIN.
    """
    print("\n" + "=" * 55)
    print("  ➕ AJOUTER UN NOUVEAU COMPTE")
    print("=" * 55)

    # Cherche le prochain numéro disponible
    comptes_existants = charger_tous_comptes()
    nouveau_num = max(comptes_existants.keys()) + 1 if comptes_existants else 1

    print(f"\n  📌 Nouveau compte : ACCOUNT{nouveau_num}")

    api_key = input("\n  API_KEY : ").strip()
    api_secret = input("  API_SECRET : ").strip()

    if not api_key or not api_secret:
        print("\n  ❌ API_KEY et API_SECRET obligatoires !")
        return

    # Sauvegarde temporaire
    set_key(ENV_FILE, f"ACCOUNT{nouveau_num}_API_KEY", api_key)
    set_key(ENV_FILE, f"ACCOUNT{nouveau_num}_API_SECRET", api_secret)

    # Connexion OAuth
    oauth_handler = tweepy.OAuth1UserHandler(
        consumer_key=api_key,
        consumer_secret=api_secret,
        callback="oob"
    )

    try:
        auth_url = oauth_handler.get_authorization_url()
    except tweepy.TweepyException as e:
        print(f"\n  ❌ Clés invalides : {e}")
        return

    print("\n  ┌─────────────────────────────────────────────────┐")
    print("  │  Ouvrez ce lien dans votre navigateur :         │")
    print(f"  │  {auth_url[:48]}  │")
    if len(auth_url) > 48:
        print(f"  │  {auth_url[48:96]}  │")
    print("  │                                                  │")
    print("  │  Connectez-vous, puis copiez le PIN.            │")
    print("  └─────────────────────────────────────────────────┘")
    print(f"\n  URL complète : {auth_url}\n")

    while True:
        pin = input("  Entrez le PIN Twitter (7 chiffres) : ").strip()
        if re.fullmatch(r"\d{7}", pin):
            break
        print("  ❌ PIN invalide, 7 chiffres requis.")

    try:
        access_token, access_token_secret = oauth_handler.get_access_token(pin)
    except tweepy.TweepyException as e:
        print(f"\n  ❌ PIN incorrect : {e}")
        return

    # Sauvegarde des tokens
    set_key(ENV_FILE, f"ACCOUNT{nouveau_num}_ACCESS_TOKEN", access_token)
    set_key(ENV_FILE, f"ACCOUNT{nouveau_num}_ACCESS_TOKEN_SECRET", access_token_secret)
    set_key(ENV_FILE, f"ACCOUNT{nouveau_num}_BEARER_TOKEN", "")

    # Vérification
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
    )

    try:
        me = client.get_me()
        username = me.data.username
        name = me.data.name
        print(f"\n  ✅ Compte ajouté : {name} (@{username})")
        print(f"     Numéro : ACCOUNT{nouveau_num}")
    except tweepy.TweepyException as e:
        print(f"\n  ⚠️  Compte ajouté mais erreur : {e}")

    print("\n  📝 Le compte est maintenant disponible au prochain lancement !\n")


def interface_interactive():
    """
    Interface terminal complète :
      1. Sélection du/des compte(s) à utiliser
      2. Option pour ajouter un nouveau compte
      3. Saisie des liens
      4. Paramètres (nb commentaires, délai, mode)
      5. Lancement
    """
    print("\n" + "=" * 70)
    print("  🤖 TWITTER BOT — Interface interactive")
    print("=" * 70)

    # ── Étape 1 : Sélection du compte ──
    comptes_dispo = charger_tous_comptes()
    
    while True:
        if comptes_dispo:
            print(f"\n  📋 COMPTES DISPONIBLES : {len(comptes_dispo)} compte(s)\n")
            for num in sorted(comptes_dispo.keys()):
                print(f"      {num}) Compte {num}")
            
            print("\n" + "─" * 70)
            print("  ℹ️  Exemples d'entrée :")
            print("      • '1'        → Un compte unique")
            print("      • '1,2,3'    → Comptes 1, 2 et 3 en PARALLÈLE 🔥")
            print("      • 'M' ou 'TOUS' → TOUS les comptes en PARALLÈLE 🔥")
            print("      • 'N'        → Ajouter un nouveau compte")
            print("─" * 70)
            
            choix = input("\n  👉 Votre choix : ").strip().upper()
            
            if choix == "N":
                print("\n" + "=" * 70)
                interface_ajouter_compte()
                print("=" * 70)
                load_dotenv(ENV_FILE, override=True)  # Recharge .env
                comptes_dispo = charger_tous_comptes()
                continue
            
            if choix in ["M", "TOUS"]:
                comptes_selectionnes = sorted(comptes_dispo.keys())
                comptes_noms = ", ".join([f"Compte {n}" for n in comptes_selectionnes])
                print(f"\n  ✅ Mode PARALLÈLE activé : {comptes_noms}")
                print("     Tous les comptes commenteront EN MÊME TEMPS ! 🔥")
                mode_multi = True
                break
            
            # Vérifier si c'est une liste de numéros séparés par des virgules
            if "," in choix:
                try:
                    nums = [int(n.strip()) for n in choix.split(",")]
                    # Vérifier que tous les numéros sont valides
                    if all(n in comptes_dispo for n in nums):
                        comptes_selectionnes = sorted(set(nums))
                        if len(comptes_selectionnes) == 1:
                            # Si seulement 1 compte, mode séquentiel
                            mode_multi = False
                            print(f"\n  ✅ Compte {comptes_selectionnes[0]} sélectionné (mode séquentiel)")
                        else:
                            # Si plusieurs comptes, mode parallèle
                            mode_multi = True
                            comptes_noms = ", ".join([f"Compte {n}" for n in comptes_selectionnes])
                            print(f"\n  ✅ Mode PARALLÈLE activé : {comptes_noms}")
                            print("     Ces comptes commenteront EN MÊME TEMPS ! 🔥")
                        break
                    else:
                        print("  ❌ Un ou plusieurs numéros invalides.")
                except ValueError:
                    print("  ❌ Format invalide. Utilisez des numéros séparés par des virgules (ex: 1,2,3).")
            else:
                # Un seul numéro
                try:
                    num = int(choix)
                    if num in comptes_dispo:
                        comptes_selectionnes = [num]
                        mode_multi = False
                        print(f"\n  ✅ Compte {num} sélectionné (mode séquentiel)")
                        break
                    else:
                        print("  ❌ Numéro invalide. Réessayez.")
                except ValueError:
                    print("  ❌ Entrée invalide (numéro, liste, M/TOUS ou N).")
        else:
            print("\n  ⚠️  AUCUN COMPTE TROUVÉ dans .env")
            print("  Voulez-vous en ajouter un maintenant ? (O/N)")
            choix = input("\n  👉 Votre choix : ").strip().upper()
            if choix == "O":
                print("\n" + "=" * 70)
                interface_ajouter_compte()
                print("=" * 70)
                load_dotenv(ENV_FILE, override=True)
                comptes_dispo = charger_tous_comptes()
            else:
                print("  Annulé.")
                return

    # Connexion du/des compte(s)
    clients = {}
    for compte_num in comptes_selectionnes:
        client, username = connecter_compte(compte_num)
        clients[compte_num] = (client, username)

    print(f"\n  ✅ {len(clients)} compte(s) connecté(s) et prêt(s) !\n")

    # ── Étape 2 : Saisie des liens ──
    print("=" * 70)
    print("  📌 Étape 2 — LIENS DES TWEETS À COMMENTER")
    print("=" * 70)
    print("  (Entrez un lien par ligne, appuyez sur ENTRÉE 2 fois pour terminer)\n")

    liens_cibles = []
    compteur = 1
    while True:
        lien = input(f"  Lien {compteur} : ").strip()
        if not lien:
            if liens_cibles:
                break
            else:
                print("  ❌ Entrez au moins un lien !")
                continue
        if lien.startswith("http"):
            liens_cibles.append(lien)
            print("       ✅ Lien accepté")
            compteur += 1
        else:
            print("       ❌ Invalide (doit commencer par http)")

    print(f"\n  ✅ {len(liens_cibles)} lien(s) enregistré(s)")

    # ── Étape 3 : Paramètres ──
    print("\n" + "=" * 70)
    print("  ⚙️  Étape 3 — PARAMÈTRES")
    print("=" * 70)

    # Nombre de commentaires par tweet
    while True:
        nb_input = input("\n  Commentaires par tweet [défaut: 1] : ").strip() or "1"
        try:
            nb_commentaires = int(nb_input)
            if 1 <= nb_commentaires <= 600:
                break
            print("  ❌ Valeur entre 1 et 600.")
        except ValueError:
            print("  ❌ Entrez un nombre entier.")

    # Délai
    delai_input = input("  Délai entre posts en secondes [défaut: 10] : ").strip() or "10"
    try:
        delai = int(delai_input)
        if delai < 5:
            delai = 5
            print("  ⚠️  Délai minimum : 5 secondes")
    except ValueError:
        delai = 10
        print("  ⚠️  Invalide, délai défini à 10s")

    # Mode
    print("\n  Mode d'exécution :")
    print("    1) 🟢 Simulation locale (sans API)")
    print("    2) 🟡 Simulation API (appels réels, sans poster)")
    print("    3) 🔴 Mode réel (POSTE VRAIMENT) ⚠️")
    mode_choice = input("\n  Votre choix (1/2/3) [défaut: 1] : ").strip() or "1"

    if mode_choice == "2":
        simulation_locale, simulation = False, True
        print("  ✅ Simulation API activée")
    elif mode_choice == "3":
        simulation_locale, simulation = False, False
        comptes_affiche = ", ".join([f"@{clients[c][1]}" for c in comptes_selectionnes])
        print(f"\n  ⚠️⚠️⚠️  MODE RÉEL ACTIVÉ ! ⚠️⚠️⚠️")
        print(f"  Les commentaires seront VRAIMENT postés depuis : {comptes_affiche}")
        confirm = input("  Confirmer ? (oui/non) : ").strip().lower()
        if confirm not in ["oui", "o", "yes", "y"]:
            print("  Annulé. Retour en simulation locale.")
            simulation_locale, simulation = True, True
        else:
            print("  ✅ Mode RÉEL confirmé !")
    else:
        simulation_locale, simulation = True, True
        print("  ✅ Simulation locale activée")

    # ── Étape 4 : Lancement ──
    print("\n" + "=" * 70)
    print("  🚀 Étape 4 — LANCEMENT")
    print("=" * 70)

    # Si mode multi, TOUS les comptes lancent en même temps
    if mode_multi:
        lancer_comptes_parallelement(
            clients=clients,
            liens=liens_cibles,
            nb_commentaires=nb_commentaires,
            delai=delai,
            simulation=simulation,
            simulation_locale=simulation_locale
        )
    else:
        # Mode simple : un seul compte
        client, compte = clients[comptes_selectionnes[0]]
        automatiser_depuis_liens(
            client=client,
            compte=compte,
            liens=liens_cibles,
            nb_commentaires=nb_commentaires,
            delai=delai,
            simulation=simulation,
            simulation_locale=simulation_locale
        )


# ──────────────────────────────────────────────
# 10. POINT D'ENTRÉE
# ──────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    
    # Affiche le menu de connexion
    if menu_connexion():
        # Si l'utilisateur s'est connecté, lance l'interface principale
        interface_interactive()
    # Sinon, le programme se termine
