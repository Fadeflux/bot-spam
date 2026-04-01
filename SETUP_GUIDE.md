# 📦 Guide d'Installation Complet

## 🚀 Démarrage Rapide

### 1️⃣ Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurer les credentials Twitter
1. Allez sur [developer.twitter.com](https://developer.twitter.com)
2. Créez une application (ou utilisez une existante)
3. Récupérez:
   - **API Key**
   - **API Secret**
   - **Bearer Token**

4. Remplissez le fichier `.env`:
```env
API_KEY=votre_clé_api
API_SECRET=votre_secret_api
BEARER_TOKEN=votre_bearer_token
```

### 3️⃣ Lancer le bot

#### Option A : Via Terminal Interactif
```bash
python twitter_bot.py
```

#### Option B : Via Dashboard Web (Recommandé)

**Terminal 1 - Lancer l'API:**
```bash
python api.py
```
L'API sera disponible sur `http://localhost:5000`

**Terminal 2 - Dashboard:**
```bash
python serve_dashboard.py
```
Ouvrez `http://localhost:8000/dashboard.html`

---

## 📝 Architecture du Projet

```
├── twitter_bot.py              # Bot principal (CLI)
├── api.py                       # API Flask REST
├── serve_dashboard.py           # Serveur web pour dashboard
├── dashboard.html               # Interface web
├── oauth_login.html             # Page OAuth
├── twitter_bot_dashboard_api.jsx # Composant React
├── accounts.json                # Stockage des comptes
├── .env                         # Configuration (credentials)
├── requirements.txt             # Dépendances Python
├── README.md                    # Documentation générale
├── README_API.md                # Documentation API
└── OAUTH_GUIDE.md              # Guide authentification
```

---

## 🔐 Authentification OAuth

Le système utilise **OAuth 1.0a** pour sécuriser l'authentification:

1. **Comptes Normaux**: Vos comptes Twitter personnels
2. **Compte Développeur**: Application créée sur developer.twitter.com (1 seule)

### Processus d'Ajout de Compte

```
User → Navigateur → /oauth_login.html
     ↓
     → Click "Commencer l'authentification"
     ↓
     → Redirection vers Twitter.com
     ↓
     → Connexion au compte cible
     ↓
     → Copie du PIN
     ↓
     → Validation dans le formulaire
     ↓
     → Compte sauvegardé dans accounts.json
```

---

## 📊 API Endpoints

### Health & Status
- `GET /api/health` - Vérifier l'API
- `GET /api/status` - État actuel du bot

### Gestion des Comptes
- `GET /api/accounts` - Lister tous les comptes
- `POST /api/accounts/add` - Ajouter un compte
- `DELETE /api/accounts/<id>` - Supprimer un compte

### Exécution
- `POST /api/launch` - Démarrer le bot
  - Body: `{"accounts": [1, 2], "tweet_id": "...", "comment": "...", "simulation": false}`
- `POST /api/stop` - Arrêter l'exécution
- `GET /api/logs` - Récupérer les logs
- `GET /api/progress` - Progression en temps réel

---

## 🐛 Troubleshooting

### Port 5000 déjà utilisé
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Port 8000 déjà utilisé
Changez le port dans `serve_dashboard.py` ligne 5

### Erreur "401 Unauthorized"
Vérifiez votre `.env`:
- Les credentials sont corrects
- Pas d'espaces avant/après les valeurs
- Le fichier n'est pas commité à Git

---

## ✅ Checklist de Vérification

- [ ] `.env` créé avec les credentials
- [ ] `pip install -r requirements.txt` exécuté
- [ ] Twitter Developer App créée
- [ ] Permissions lues/écriture activées
- [ ] Comptes ajoutés via OAuth
- [ ] API répond `200 OK` sur `/api/health`
- [ ] Dashboard accessible sur localhost:8000
