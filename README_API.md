# 🐦 Twitter Bot - Système Complet

## 📋 Contenu

### 1. **twitter_bot.py** (Backend Principal)
- Bot Twitter/X complet
- Gestion des comptes multiples
- Menu interactif en terminal
- OAuth 1.0a authentification
- Support simulation + mode réel

**Utilisation :**
```bash
python twitter_bot.py
```

### 2. **api.py** (API REST Flask)
- Serveur Flask sur `http://localhost:5000`
- Communication avec le dashboard React
- Endpoints RESTful pour tous les contrôles
- Gestion asynchrone des lancements

**Installation des dépendances :**
```bash
pip install flask flask-cors
```

**Lancement :**
```bash
python api.py
```

APIs disponibles :
- `GET /api/health` - Vérification de santé
- `GET /api/accounts` - Lister les comptes
- `POST /api/accounts/add` - Ajouter un compte
- `DELETE /api/accounts/<id>` - Supprimer un compte
- `POST /api/launch` - Lancer le bot
- `POST /api/stop` - Arrêter l'exécution
- `GET /api/status` - État actuel
- `GET /api/logs` - Récupérer les logs

### 3. **twitter_bot_dashboard_api.jsx** (Frontend React)
- Interface graphique complète
- Gestion des comptes
- Configuration du lancement
- Monitoring en temps réel
- Terminal avec logs

**Caractéristiques :**
- ✅ Connexion live à l'API Flask
- ✅ Sélection multiple des comptes
- ✅ Configuration complète des paramètres
- ✅ Logs en temps réel
- ✅ Barre de progression
- ✅ Mode simulation + mode réel

## 🚀 Utilisation Complète

### Option 1 : En Terminal (sans interface)
```bash
python twitter_bot.py
```
- Menu interactif complet
- Connexion manuelle à des comptes
- Lancement direct depuis le terminal

### Option 2 : Avec Dashboard (Recommandé)

**Terminal 1 - Lancer le server API :**
```bash
python api.py
```
Output :
```
======================================================================
  🚀 API TWITTER BOT - Flask Server
======================================================================
  📍 Serveur : http://localhost:5000
  📊 Docs : GET http://localhost:5000
======================================================================
```

**Terminal 2 - Servir le dashboard :**
```bash
npx create-react-app dashboard
# Copier twitter_bot_dashboard_api.jsx dans src/App.jsx
npm start
```

Puis ouvrir `http://localhost:3000`

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│   Dashboard React (Frontend)                 │
│  - Gestion des comptes                       │
│  - Configuration                             │
│  - Monitoring temps réel                     │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
        ┌──────────▼──────────┐
        │  API Flask (api.py)  │
        │  - Endpoints REST    │
        │  - Gestion état      │
        │  - Logging           │
        └──────────┬───────────┘
                   │ Import/Functions
        ┌──────────▼──────────────────┐
        │  Twitter Bot (twitter_bot.py)│
        │  - Core intelligence         │
        │  - OAuth Tweepy              │
        │  - Multi-account support     │
        └──────────────────────────────┘
```

## 🔐 Sécurité

- ✅ Tokens sauvegardés localement dans `.env`
- ✅ API accessible uniquement en localhost par défaut
- ✅ CORS activé pour développement
- ✅ Pas de stockage de credentials en mémoire persistante

## 🧪 Tests

```bash
python test_api.py
```

Vérifie :
- ✅ Serveur API en ligne
- ✅ Endpoints opérationnels
- ✅ Comptes chargés

## ⚙️ Configuration

### Fichier `.env`

Créé automatiquement lors de l'ajout de comptes :

```env
# Format pour compte unique (legacy)
API_KEY=xxxx
API_SECRET=xxxx
ACCESS_TOKEN=xxxx
ACCESS_TOKEN_SECRET=xxxx

# Format pour multiples comptes
ACCOUNT1_API_KEY=xxxx
ACCOUNT1_API_SECRET=xxxx
ACCOUNT1_ACCESS_TOKEN=xxxx
ACCOUNT1_ACCESS_TOKEN_SECRET=xxxx

ACCOUNT2_API_KEY=xxxx
ACCOUNT2_API_SECRET=xxxx
...
```

## 📝 Flux Utilisateur

### Via Dashboard :
1. Ouvrir http://localhost:3000
2. Aller à "Comptes" 
3. Ajouter/Sélectionner des comptes
4. Aller à "Lancement"
5. Entrer les tweets cibles
6. Configurer les paramètres
7. Lancer en mode simulation ou réel
8. Monitorer en temps réel dans "Monitor"

### Via Terminal :
1. `python twitter_bot.py`
2. Répondre aux prompts
3. Sélectionner les comptes
4. Entrer les liens
5. Configurer les paramètres
6. Lancer

## 🔄 Conversion Terminal → Dashboard

Si vous avez commencé avec le terminal, le dashboard détectera automatiquement vos comptes existants dans `.env` et vous pourrez les utiliser immédiatement !

## 🐛 Troubleshooting

### "API not connected"
- Vérifier que `python api.py` est lancé
- Vérifier http://localhost:5000/api/health
- Vérifier les logs Flask

### "Aucun compte trouvé"
- Ajouter des comptes via le dashboard ou le terminal
- Vérifier le fichier `.env`

### "Token invalide"
- Les tokens Twitter expirent
- Supprimer le compte et le reconnecter via OAuth

## 📚 Ressources

- [Tweepy Docs](https://docs.tweepy.org)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Flask Docs](https://flask.palletsprojects.com)

---

**Version :** 1.0.0  
**Dernière mise à jour :** Mars 2026
