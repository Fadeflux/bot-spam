# 🐦 Guide d'Authentification - Twitter Bot

## Vue d'ensemble

Vous avez maintenant une **API OAuth complète** pour connecter vos comptes normaux (non-développeur) au bot. Voici comment ça fonctionne:

---

## 🔐 Configuration préalable requise

### 1. Obtenir vos credentials de développeur

✅ Vous devez **créer UNE SEULE application** sur [developer.twitter.com](https://developer.twitter.com)

Dans le Dashboard > Keys and Tokens, récupérez:
```
API_KEY = votre_api_key
API_SECRET = votre_api_secret
BEARER_TOKEN = votre_bearer_token
```

### 2. Créer le fichier `.env`

À la racine de votre projet, créez un fichier `.env` avec **SEULEMENT** les credentials développeur:

```env
# Credentials du compte DÉVELOPPEUR (1 seul)
API_KEY=votre_api_key_ici
API_SECRET=votre_api_secret_ici
BEARER_TOKEN=votre_bearer_token_ici
```

⚠️ **N'y mettez PAS** les Access Token/Secret - ils seront générés automatiquement !

---

## 🚀 Connecter vos comptes

### Via l'interface web (RECOMMANDÉ)

1. **Lancez l'API**
```bash
python api.py
```

2. **Ouvrez dans votre navigateur**
```
http://localhost:5000/oauth_login.html
```

3. **Suivez les 3 étapes**:
   - ➡️ Cliquez "Commencer l'authentification"
   - ➡️ Ouvrez le lien Twitter et autorisez l'application
   - ➡️ Copiez le PIN et collez-le dans le formulaire

4. **C'est fait !** ✅ Votre compte est connecté

---

### Via l'API directement

#### Étape 1: Initialiser OAuth
```bash
curl -X POST http://localhost:5000/api/oauth/start \
  -H "Content-Type: application/json" \
  -d '{"account_number": 1}'
```

**Réponse:**
```json
{
  "success": true,
  "auth_url": "https://twitter.com/i/oauth2/authorize?...",
  "session_id": "abc-123-def-456",
  "account_number": 1
}
```

#### Étape 2: Ouvrir `auth_url` dans le navigateur

Connectez-vous au compte qui doit poster les commentaires.

#### Étape 3: Valider le PIN
```bash
curl -X POST http://localhost:5000/api/oauth/complete \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def-456",
    "pin": "1234567"
  }'
```

**Réponse:**
```json
{
  "success": true,
  "message": "Compte John Doe (@john_doe) authentifié avec succès !",
  "username": "john_doe",
  "accounts": [
    {"id": 1, "name": "Compte 1", "status": "connected"}
  ]
}
```

---

## 📋 Structure des comptes

Votre `.env` sera automatiquement rempli comme ça:

```env
# Credentials du développeur (requis)
API_KEY=xxx
API_SECRET=xxx
BEARER_TOKEN=xxx

# Compte 1 (connecté via OAuth)
ACCOUNT1_API_KEY=xxx
ACCOUNT1_API_SECRET=xxx
ACCOUNT1_ACCESS_TOKEN=auto_generated_1
ACCOUNT1_ACCESS_TOKEN_SECRET=auto_generated_1
ACCOUNT1_BEARER_TOKEN=xxx

# Compte 2 (connecté via OAuth)
ACCOUNT2_API_KEY=xxx
ACCOUNT2_API_SECRET=xxx
ACCOUNT2_ACCESS_TOKEN=auto_generated_2
ACCOUNT2_ACCESS_TOKEN_SECRET=auto_generated_2
ACCOUNT2_BEARER_TOKEN=xxx

# ... etc pour chaque compte
```

---

## ✨ Utiliser les comptes pour poster

### Via l'API de lancement

```bash
curl -X POST http://localhost:5000/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "account_ids": [1, 2, 3],
    "links": [
      "https://x.com/user/status/123456789",
      "https://x.com/user/status/987654321"
    ],
    "nb_comments": 1,
    "delay": 5,
    "mode": "real"
  }'
```

Le bot va maintenant poster des commentaires avec **les 3 comptes** que vous avez connectés !

---

## 🔄 Gérer les comptes

### Voir tous les comptes connectés
```bash
curl http://localhost:5000/api/accounts
```

### Supprimer un compte
```bash
curl -X DELETE http://localhost:5000/api/accounts/1
```

---

## ❓ FAQ

### Q: Je peux utiliser le même compte développeur pour plusieurs apps ?
**Non.** Vous devez créer UN compte développeur par application.

### Q: Mes autres comptes doivent être développeur ?
**Non !** Seul le compte qui crée l'application doit être développeur. Les autres peuvent être des comptes normaux.

### Q: Le PIN expirer après combien de temps ?
**30 minutes** généralement. Si ça expire, recommencez à l'étape 1.

### Q: Où se trouvent mes tokens sauvegardés ?
Dans le fichier `.env` à la racine du projet.

### Q: Je peux connecter combien de comptes ?
**Illimité !** Le système supporte autant de comptes que vous voulez.

### Q: Comment je teste sans vraiment poster ?
Utilisez le `mode: "sim"` dans le payload de `/api/launch`:
```json
{
  "account_ids": [1, 2],
  "links": [...],
  "mode": "sim"  // Production: "real"
}
```

---

## 🛠️ Dépannage

### "API_KEY ou API_SECRET manquants"
✅ Vérifiez votre `.env` contient les credentials du développeur

### "PIN incorrect ou expiré"
✅ Réessayez - génération d'une nouvelle URL OAuth

### "Session OAuth expirée"
✅ Redémarrez depuis l'étape 1

### "Impossible de générer l'URL OAuth"
✅ Vérifiez vos API_KEY et API_SECRET (elles doivent être valides)

---

## 📞 Support

Si vous avez des problèmes:
1. Vérifiez les logs dans le terminal
2. Assurez-vous que `api.py` et `twitter_bot.py` sont dans le même dossier
3. Vérifiez votre `.env` avec les credentials correction

Bon succès ! 🚀
