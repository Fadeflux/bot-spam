"""
=============================================================
  API REST FLASK - Twitter Bot
  Connexion entre Dashboard React et Bot Python
=============================================================
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv, set_key
import os
import json
import threading
import time
from datetime import datetime
import queue

# Import des fonctions du bot
from twitter_bot import (
    charger_tous_comptes,
    connecter_compte,
    automatiser_depuis_liens,
    generer_commentaire,
    extraire_id_depuis_lien,
    generer_url_oauth,
    valider_pin_oauth
)

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

ENV_FILE = ".env"
load_dotenv(ENV_FILE)

# ── Global state ──
app_state = {
    "running": False,
    "progress": 0,
    "logs": [],
    "accounts": {},
    "stop_requested": False
}

logs_queue = queue.Queue()
MAX_LOGS = 500


# ──────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────

def add_log(msg, log_type="info"):
    """Ajoute un message de log."""
    log_entry = {
        "msg": msg,
        "type": log_type,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    app_state["logs"].append(log_entry)
    if len(app_state["logs"]) > MAX_LOGS:
        app_state["logs"].pop(0)
    logs_queue.put(log_entry)
    print(f"[{log_type.upper()}] {msg}")


def get_account_status(account_id):
    """Récupère le statut d'un compte."""
    comptes = charger_tous_comptes()
    if account_id in comptes:
        compte = comptes[account_id]
        return {
            "id": account_id,
            "exists": True,
            "has_token": bool(compte.get("access_token"))
        }
    return {"id": account_id, "exists": False}


# ──────────────────────────────────────────────
# ENDPOINTS - ACCOUNTS
# ──────────────────────────────────────────────

@app.route("/api/accounts", methods=["GET"])
def get_accounts():
    """Récupère tous les comptes disponibles."""
    try:
        comptes = charger_tous_comptes()
        result = []
        
        for num in sorted(comptes.keys()):
            compte = comptes[num]
            result.append({
                "id": num,
                "name": f"Compte {num}",
                "has_credentials": bool(compte.get("api_key") and compte.get("api_secret")),
                "has_tokens": bool(compte.get("access_token")),
                "status": "connected" if compte.get("access_token") else "auth_pending"
            })
        
        add_log(f"Comptes chargés : {len(result)}", "info")
        return jsonify({"success": True, "accounts": result, "count": len(result)}), 200
    
    except Exception as e:
        add_log(f"Erreur lors du chargement des comptes : {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/accounts/add", methods=["POST"])
def add_account():
    """
    Ajoute un nouveau compte.
    Body: {
        "api_key": "xxx",
        "api_secret": "xxx",
        "access_token": "xxx",
        "access_token_secret": "xxx"
    }
    """
    try:
        data = request.json
        required = ["api_key", "api_secret", "access_token", "access_token_secret"]
        
        if not all(k in data for k in required):
            return jsonify({"success": False, "error": "Champs manquants"}), 400
        
        # Trouve le prochain numéro disponible
        comptes_existants = charger_tous_comptes()
        nouveau_num = max(comptes_existants.keys()) + 1 if comptes_existants else 1
        
        prefix = f"ACCOUNT{nouveau_num}_"
        
        # Sauvegarde les credentials
        set_key(ENV_FILE, f"{prefix}API_KEY", data["api_key"])
        set_key(ENV_FILE, f"{prefix}API_SECRET", data["api_secret"])
        set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN", data["access_token"])
        set_key(ENV_FILE, f"{prefix}ACCESS_TOKEN_SECRET", data["access_token_secret"])
        set_key(ENV_FILE, f"{prefix}BEARER_TOKEN", "")
        
        # Recharge .env
        load_dotenv(ENV_FILE, override=True)
        
        add_log(f"✅ Compte {nouveau_num} ajouté", "ok")
        
        return jsonify({
            "success": True,
            "message": f"Compte {nouveau_num} ajouté avec succès",
            "account_id": nouveau_num
        }), 201
    
    except Exception as e:
        add_log(f"Erreur lors de l'ajout du compte : {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Supprime un compte."""
    try:
        prefix = f"ACCOUNT{account_id}_"
        
        # Supprime les clés du compte
        for key in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET", "BEARER_TOKEN"]:
            env_key = f"{prefix}{key}"
            if os.getenv(env_key):
                set_key(ENV_FILE, env_key, "")
        
        load_dotenv(ENV_FILE, override=True)
        
        add_log(f"✅ Compte {account_id} supprimé", "ok")
        
        return jsonify({"success": True, "message": "Compte supprimé"}), 200
    
    except Exception as e:
        add_log(f"Erreur lors de la suppression : {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


# ──────────────────────────────────────────────
# ENDPOINTS - RUNNER
# ──────────────────────────────────────────────

@app.route("/api/launch", methods=["POST"])
def launch():
    """
    Lance le bot avec les paramètres.
    Body: {
        "account_ids": [1, 2],
        "links": ["https://x.com/.../1234567890", ...],
        "nb_comments": 1,
        "delay": 5,
        "mode": "sim" ou "real"
    }
    """
    try:
        if app_state["running"]:
            return jsonify({"success": False, "error": "Un lancement est déjà en cours"}), 400
        
        data = request.json
        account_ids = data.get("account_ids", [])
        links = data.get("links", [])
        nb_comments = data.get("nb_comments", 1)
        delay = data.get("delay", 5)
        mode = data.get("mode", "sim")
        
        if not account_ids:
            return jsonify({"success": False, "error": "Aucun compte sélectionné"}), 400
        
        if not links:
            return jsonify({"success": False, "error": "Aucun lien fourni"}), 400
        
        # Valide les liens
        valid_links = [l for l in links if extraire_id_depuis_lien(l)]
        if not valid_links:
            return jsonify({"success": False, "error": "Aucun lien valide"}), 400
        
        # Lance en thread
        app_state["running"] = True
        app_state["progress"] = 0
        app_state["logs"] = []
        app_state["stop_requested"] = False
        
        thread = threading.Thread(
            target=_launch_worker,
            args=(account_ids, valid_links, nb_comments, delay, mode),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Lancement initialisé",
            "accounts": len(account_ids),
            "links": len(valid_links),
            "mode": mode
        }), 200
    
    except Exception as e:
        app_state["running"] = False
        add_log(f"Erreur lors du lancement : {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


def _launch_worker(account_ids, links, nb_comments, delay, mode):
    """Worker thread pour lancer le bot."""
    try:
        simulation = mode == "sim"
        simulation_locale = mode == "sim"
        
        add_log(f"🚀 Lancement — {len(account_ids)} compte(s), {len(links)} tweet(s)", "info")
        add_log(f"Mode: {'🔴 RÉEL' if not simulation else '🟡 SIMULATION'}", "warn" if not simulation else "info")
        
        total_posts = len(account_ids) * len(links) * nb_comments
        done = 0
        
        # Charge et connecte les comptes
        comptes_dispo = charger_tous_comptes()
        clients = {}
        
        for account_id in account_ids:
            try:
                add_log(f"Connexion au compte {account_id}...", "info")
                client, username = connecter_compte(account_id)
                clients[account_id] = (client, username)
                add_log(f"✅ Compte {account_id} connecté (@{username})", "ok")
            except Exception as e:
                add_log(f"❌ Erreur connexion compte {account_id}: {str(e)}", "err")
                continue
        
        if not clients:
            add_log("❌ Aucun compte connecté", "err")
            app_state["running"] = False
            return
        
        # Lancement principal
        for account_id, (client, username) in clients.items():
            if app_state["stop_requested"]:
                break
            
            for link in links:
                if app_state["stop_requested"]:
                    break
                
                tweet_id = extraire_id_depuis_lien(link)
                if not tweet_id:
                    add_log(f"[{username}] ❌ Lien invalide", "err")
                    continue
                
                add_log(f"[{username}] 🔗 Tweet: {tweet_id}", "info")
                
                for j in range(nb_comments):
                    if app_state["stop_requested"]:
                        break
                    
                    time.sleep(delay)
                    comment = generer_commentaire("", modele="contextuel")
                    
                    if not simulation_locale:
                        try:
                            response = client.create_tweet(
                                text=comment,
                                in_reply_to_tweet_id=tweet_id
                            )
                            add_log(f"[{username}] ✅ Posté: {comment[:50]}...", "ok")
                        except Exception as e:
                            add_log(f"[{username}] ❌ Erreur: {str(e)}", "err")
                    else:
                        add_log(f"[{username}] 💬 [SIM] {comment[:50]}...", "warn")
                    
                    done += 1
                    app_state["progress"] = int((done / total_posts) * 100)
        
        add_log(f"✅ Terminé ! {done}/{total_posts} commentaires", "ok")
        app_state["running"] = False
    
    except Exception as e:
        add_log(f"❌ Erreur worker: {str(e)}", "err")
        app_state["running"] = False


@app.route("/api/stop", methods=["POST"])
def stop():
    """Arrête l'exécution en cours."""
    try:
        if not app_state["running"]:
            return jsonify({"success": False, "error": "Aucun lancement en cours"}), 400
        
        app_state["stop_requested"] = True
        add_log("⛔ Arrêt demandé", "warn")
        
        return jsonify({"success": True, "message": "Arrêt initié"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ──────────────────────────────────────────────
# ENDPOINTS - STATUS & LOGS
# ──────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def get_status():
    """Récupère le statut général."""
    return jsonify({
        "running": app_state["running"],
        "progress": app_state["progress"],
        "logs_count": len(app_state["logs"])
    }), 200


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Récupère tous les logs."""
    limit = request.args.get("limit", 100, type=int)
    return jsonify({
        "logs": app_state["logs"][-limit:],
        "total": len(app_state["logs"])
    }), 200


@app.route("/api/logs/stream", methods=["GET"])
def stream_logs():
    """Stream les logs (SSE - Server Sent Events)."""
    def generate():
        last_index = 0
        while True:
            current_logs = app_state["logs"]
            if len(current_logs) > last_index:
                for log in current_logs[last_index:]:
                    yield f"data: {json.dumps(log)}\n\n"
                last_index = len(current_logs)
            
            if not app_state["running"]:
                yield f"data: {json.dumps({'msg': 'STREAM_END', 'type': 'info'})}\n\n"
                break
            
            time.sleep(0.5)
    
    return app.response_class(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# ──────────────────────────────────────────────
# ENDPOINTS - OAUTH AUTHENTICATION
# ──────────────────────────────────────────────

@app.route("/api/oauth/start", methods=["POST"])
def oauth_start():
    """
    Initie le processus OAuth.
    Retourne l'URL que l'utilisateur doit ouvrir.
    
    Body: {
        "account_number": 1  (optionnel)
    }
    """
    try:
        data = request.json or {}
        account_num = data.get("account_number")
        
        # Détermine le prochain numero de compte si non fourni
        if not account_num:
            comptes = charger_tous_comptes()
            account_num = max(comptes.keys()) + 1 if comptes else 1
        
        auth_url, session_id = generer_url_oauth(account_num)
        
        add_log(f"OAuth initié pour compte {account_num}", "info")
        
        return jsonify({
            "success": True,
            "auth_url": auth_url,
            "session_id": session_id,
            "account_number": account_num,
            "message": f"Ouvrez l'URL et connectez-vous avec le compte qui doit poster les commentaires"
        }), 200
    
    except Exception as e:
        add_log(f"Erreur OAuth start: {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/oauth/complete", methods=["POST"])
def oauth_complete():
    """
    Complète le processus OAuth avec le PIN.
    
    Body: {
        "session_id": "uuid",
        "pin": "1234567"
    }
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        pin = data.get("pin", "").strip()
        
        if not session_id or not pin:
            return jsonify({
                "success": False,
                "error": "session_id et pin requis"
            }), 400
        
        access_token, access_token_secret, username, message = valider_pin_oauth(session_id, pin)
        
        add_log(f"✅ Compte authentifié : @{username}", "ok")
        
        # Recharge les comptes pour obtenir le nouveau compte
        all_accounts = charger_tous_comptes()
        
        return jsonify({
            "success": True,
            "message": message,
            "username": username,
            "accounts": [
                {
                    "id": num,
                    "name": f"Compte {num}",
                    "has_credentials": True,
                    "has_tokens": True,
                    "status": "connected"
                }
                for num in sorted(all_accounts.keys())
            ]
        }), 200
    
    except ValueError as e:
        add_log(f"Erreur validation PIN: {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 400
    
    except Exception as e:
        add_log(f"Erreur OAuth complete: {str(e)}", "err")
        return jsonify({"success": False, "error": str(e)}), 500


# ──────────────────────────────────────────────
# ENDPOINTS - HEALTH
# ──────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Vérification de santé de l'API."""
    return jsonify({
        "status": "ok",
        "running": app_state["running"],
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────

@app.route("/oauth_login.html", methods=["GET"])
def oauth_login():
    """Sert la page d'authentification OAuth."""
    try:
        return send_from_directory(".", "oauth_login.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/test_oauth.html", methods=["GET"])
def test_oauth():
    """Sert la page de test OAuth."""
    try:
        return send_from_directory(".", "test_oauth.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/dashboard.html", methods=["GET"])
def dashboard():
    """Sert la page du dashboard."""
    try:
        return send_from_directory(".", "dashboard.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/", methods=["GET"])
def home():
    """Accueil - lien vers les endpoints."""
    return jsonify({
        "name": "Twitter Bot API",
        "version": "1.0.0",
        "links": {
            "oauth_login": "/oauth_login.html",
            "dashboard": "/dashboard.html"
        },
        "endpoints": {
            "accounts": "GET /api/accounts",
            "add_account": "POST /api/accounts/add",
            "delete_account": "DELETE /api/accounts/<id>",
            "launch": "POST /api/launch",
            "stop": "POST /api/stop",
            "status": "GET /api/status",
            "logs": "GET /api/logs",
            "oauth_start": "POST /api/oauth/start",
            "oauth_complete": "POST /api/oauth/complete",
            "health": "GET /api/health"
        }
    }), 200


# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# ERROR HANDLERS
# ──────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint non trouvé"}), 404


@app.errorhandler(500)
def internal_error(e):
    add_log(f"Erreur 500: {str(e)}", "err")
    return jsonify({"success": False, "error": "Erreur serveur"}), 500


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    print("\n" + "="*70)
    print("  🚀 API TWITTER BOT - Flask Server")
    print("="*70)
    print("  📍 Serveur : http://localhost:5000")
    print("  📊 Docs : GET http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
