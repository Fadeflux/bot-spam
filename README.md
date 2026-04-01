# 🤖 Twitter Bot - Automatisation de Commentaires (MULTI-COMPTES & PARALLÈLE)

## 📖 Vue d'ensemble

Ce bot automatise la publication de commentaires (replies) sur des tweets Twitter/X en utilisant l'API v2.

**✨ Nouvelles fonctionnalités :**
- 🔄 **Support illimité de comptes** (pas de limite 1-9)
- ⚡ **Exécution parallèle** - Tous les comptes commentent EN MÊME TEMPS
- ➕ **Ajouter des comptes directement du bot** (interface intuitive)
- 📊 **Résumé détaillé** de chaque compte après exécution

---

## 🛠️ Installation

### 1. Prérequis
- Python 3.8+
- Compte Twitter Developer (gratuit)

### 2. Installer les dépendances
```bash
pip install tweepy python-dotenv
```

### 3. Créer le fichier `.env` (optionnel au démarrage)
Vous pouvez créer un fichier `.env` à la racine avec vos clés API :

```env
# Application Twitter (UNIQUE - partagée pour tous les comptes)
API_KEY=votre_clé_api
API_SECRET=votre_secret_api
BEARER_TOKEN=votre_bearer_token
```

💡 Les tokens d'accès pour chaque compte seront **générés automatiquement** (pas besoin de les mettre dans .env au départ)

---

## 🚀 Lancer le bot

```bash
python twitter_bot.py
```

---

## 📋 Guide étape par étape

### **Étape 1 : Sélectionner ou ajouter des comptes**

```
======================================================================
  🤖 TWITTER BOT — Interface interactive
======================================================================

  📋 COMPTES DISPONIBLES : 2 compte(s)

      1) Compte 1
      2) Compte 2

──────────────────────────────────────────────────────────────────────
  OPTIONS :
      M) 🔄 Utiliser TOUS les comptes (commentaire parallèle) ⚡
      N) ➕ AJOUTER UN NOUVEAU COMPTE
──────────────────────────────────────────────────────────────────────

  👉 Votre choix (numéro/M/N) : 
```

**Options :**
- **Tapez un numéro** (ex: `1`) → Utiliser UN compte seul
- **Tapez M** → Utiliser TOUS les comptes EN PARALLÈLE ⚡
- **Tapez N** → AJOUTER un nouveau compte

### **AJOUTER UN NOUVEAU COMPTE (Option N)**

```
======================================================================
  ➕ AJOUTER UN NOUVEAU COMPTE
======================================================================

  📌 Nouveau compte : ACCOUNT3

  API_KEY : [entrez votre clé API]
  API_SECRET : [entrez votre secret API]
  
  ┌─────────────────────────────────────────────┐
  │  Ouvrez ce lien dans votre navigateur :     │
  │  https://twitter.com/i/oauth2/authorize... │
  │                                              │
  │  Connectez-vous, puis copiez le PIN.        │
  └─────────────────────────────────────────────┘

  Entrez le PIN Twitter (7 chiffres) : [entrez le PIN]
  
  ✅ Compte ajouté : YourName (@yourname)
     Numéro : ACCOUNT3

  📝 Le compte est maintenant disponible au prochain lancement !
```

Le compte est **sauvegardé automatiquement** dans `.env` 🎉

### **Étape 2 : Entrer les liens des tweets**

```
======================================================================
  📌 Étape 2 — LIENS DES TWEETS À COMMENTER
======================================================================
  (Entrez un lien par ligne, appuyez sur ENTRÉE 2 fois pour terminer)

  Lien 1 : https://twitter.com/user/status/1234567890
       ✅ Lien accepté
  Lien 2 : https://twitter.com/user/status/9876543210
       ✅ Lien accepté
  Lien 3 : 
  
  ✅ 2 lien(s) enregistré(s)
```

### **Étape 3 : Configurer les paramètres**

```
======================================================================
  ⚙️  Étape 3 — PARAMÈTRES
======================================================================

  Commentaires par tweet [défaut: 1] : 1
  Délai entre posts en secondes [défaut: 10] : 10

  Mode d'exécution :
    1) 🟢 Simulation locale (sans API)
    2) 🟡 Simulation API (appels réels, sans poster)
    3) 🔴 Mode réel (POSTE VRAIMENT) ⚠️

  Votre choix (1/2/3) [défaut: 1] : 1
  ✅ Simulation locale activée
```

**Modes :**
- **1** (Défaut) = Test sans appels API
- **2** = Teste l'API mais ne poste pas
- **3** = POSTE VRAIMENT (confirmer avant)

### **Étape 4 : Lancement parallèle**

#### Avec **Mode séquentiel** (1 compte) :
```
======================================================================
  🤖 AUTOMATISATION DE COMMENTAIRES - Twitter/X
======================================================================
  Compte       : @account1
  Mode         : 🟢 SIMULATION LOCALE
  Nb liens     : 2
  Commentaires : 1 par tweet
  Total prévu  : 2 commentaire(s)
======================================================================

📌 Post 1/2
   Lien : https://twitter.com/user/status/1234567890
   🔗 ID extrait : 1234567890
   ✅ Tweet simulé : Excellentes performances...
   [SIM LOCAL] 💬 @account1 → 'Great content, love this 🔥'

📌 Post 2/2
   ...
   
✅ Terminé ! 2/2 commentaire(s) traité(s)
```

#### Avec **Mode parallèle M** (TOUS les comptes EN MÊME TEMPS) ⚡ :
```
======================================================================
  🚀 LANCEMENT PARALLÈLE - Tous les comptes COMMENTENT EN MÊME TEMPS !
======================================================================

   📊 Configuration :
      • Nombre de comptes      : 3
      • Nombre de tweets       : 2
      • Commentaires/tweet     : 1
      • Délai entre posts      : 10s
      • Total de commentaires  : 6

======================================================================

   🔵 [@account1] DÉMARRAGE → Poste des commentaires...
   🔵 [@account2] DÉMARRAGE → Poste des commentaires...
   🔵 [@account3] DÉMARRAGE → Poste des commentaires...
   
   ⏳ Tous les comptes travaillent en parallèle...
   
   👉 PENDANT CE TEMPS : Tous les comptes postent EN MÊME TEMPS ⚡
   
   [30-60 secondes plus tard...]
   
   ✅ [@account1] TERMINÉ → Tous les commentaires sont postés !
   ✅ [@account2] TERMINÉ → Tous les commentaires sont postés !
   ✅ [@account3] TERMINÉ → Tous les commentaires sont postés !

======================================================================
  ✅ RÉSUMÉ FINAL - TOUS LES COMPTES ONT TERMINÉ !
======================================================================

   ✅ @account1 → 2 commentaire(s) traité(s)
   ✅ @account2 → 2 commentaire(s) traité(s)
   ✅ @account3 → 2 commentaire(s) traité(s)

   ──────────────────────────────────────────────────────────────────
   📊 TOTAL : 6 commentaire(s) postés par 3 compte(s)
======================================================================
```

---

## ⚡ Comparaison : Séquentiel vs Parallèle

| Scénario | Comptes | Tweets | Mode | Temps |
|----------|---------|--------|------|-------|
| Séquentiel | 3 | 5 | 1-à-1 | ~150s |
| **Parallèle** | **3** | **5** | **M** | **~50s** |

**⚡ 3× plus rapide avec le mode parallèle !**

---

## 📝 Structure `.env` avec plusieurs comptes

```env
# Application Twitter (UNIQUE - pour tous les comptes)
API_KEY=votre_clé
API_SECRET=votre_secret
BEARER_TOKEN=votre_bearer

# Compte 1 (généré automatiquement après 1er lancement)
ACCOUNT1_API_KEY=clé1
ACCOUNT1_API_SECRET=secret1
ACCOUNT1_ACCESS_TOKEN=token1
ACCOUNT1_ACCESS_TOKEN_SECRET=token_secret1
ACCOUNT1_BEARER_TOKEN=bearer1

# Compte 2 (généré automatiquement)
ACCOUNT2_API_KEY=clé2
ACCOUNT2_API_SECRET=secret2
ACCOUNT2_ACCESS_TOKEN=token2
ACCOUNT2_ACCESS_TOKEN_SECRET=token_secret2
ACCOUNT2_BEARER_TOKEN=bearer2

# Compte 3, 4, 5... (autant que vous voulez ! ∞)
...
```

**⚠️ Vous n'ajoutez PAS les clés manuellement.**
Le bot génère tout via OAuth PIN à chaque nouveau compte.

---

## 🔑 Obtenir vos clés API Twitter

1. Allez sur [developer.twitter.com](https://developer.twitter.com)
2. Créez/connectez à votre compte Developer
3. Créez une **application** (Project > Create App)
4. Allez dans **Settings** → **Keys and Tokens**
5. Générez les **API Key**, **API Secret**, **Bearer Token**
6. Mettez-les dans `.env`

C'est **gratuit** (et aucun abonnement n'est nécessaire pour les API keys) 🎉

---

## ⚠️ Limitations et bonnes pratiques

- **Rate limiting API** : Twitter limite les appels. Respectez un délai minimum de 5 secondes
- **Détection de spam** : Ne postez pas plus de 100 commentaires par heure par compte
- **Authentification** : Les tokens d'accès expirent après 2 ans
- **Simulation locale** : Testez toujours en mode 1 (simulation) avant mode 3 (réel)

---

## 🐛 Dépannage

### "API_KEY et API_SECRET manquants"
→ Créez un fichier `.env` avec vos clés API (voir section Installation)

### "PIN incorrect ou expiré"
→ Le PIN Twitter expire après ~15 minutes. Réessayez

### "Token invalide"
→ Supprimez les tokens de `.env` et relancez le bot

### "Rate limit exceeded"
→ Les appels API sont limités. Attendez quelques minutes ou augmentez le délai

---

## 📞 Support

Si vous rencontrez un problème :
1. Vérifiez votre fichier `.env`
2. Testez en mode simulation (option 1)
3. Vérifiez que vos clés API sont valides sur [developer.twitter.com](https://developer.twitter.com)
- Une URL par ligne
- Ligne vide pour terminer

**Formats acceptés :**
```
https://twitter.com/user/status/1234567890
https://x.com/user/status/1234567890
https://mobile.twitter.com/user/status/1234567890
```

### Étape 3️⃣ : Paramètres
- **Commentaires par tweet** : 1-10 (défaut: 1)
- **Délai entre posts** : secondes (min: 5s, défaut: 10s)
- **Mode d'exécution** :
  - 🟢 **Simulation locale** : Teste sans appel API
  - 🟡 **Simulation API** : Appels réels mais pas de post
  - 🔴 **Mode réel** : Poste VRAIMENT sur Twitter

### Étape 4️⃣ : Lancement
Le bot :
1. Extrait l'ID du tweet depuis le lien
2. Récupère le contenu du tweet
3. Génère un commentaire unique (combinaisons aléatoires)
4. Poste le commentaire (selon le mode choisi)
5. Attend le délai configuré
6. Recommence pour le prochain tweet

---

## 💬 Génération de commentaires

Les commentaires sont générés par **combinaison aléatoire** de trois segments :

### Format
```
[Début] [Milieu], [Fin]
```

### Exemples
- "Great content, thanks for sharing! 🙌"
- "Awesome resource, love this 🔥"
- "Excellent approach, well done! 👍"
- "Fantastic post, super helpful 💡"
- "Incredible analysis, keep it up! 🚀"

Chaque commentaire est unique !

---

## 📊 Résultat final

Le bot affiche un résumé :
- ✅ Nombre de commentaires traités
- 📤 Compte source
- 📋 Liste des liens avec statut (ID du post ou "simulé")

---

## ⚠️ Points importants

### Rate Limiting
Twitter limite les appels API. Le bot gère automatiquement les délais d'attente.

### Délai minimum
Minimum **5 secondes** entre les posts (Twitter peut bloquer les spams)

### Tokens
- Les **Access Tokens** sont générés une seule fois via OAuth
- Ils sont sauvegardés dans `.env` automatiquement
- Les prochains lancements n'auront pas besoin du flow OAuth

### Mode simulation
Utilisez le mode simulation pour **tester gratuitement** avant le mode réel !

---

## 🐛 Troubleshooting

| Erreur | Solution |
|--------|----------|
| `API_KEY et API_SECRET manquants` | Remplissez le `.env` avec vos clés |
| `PIN incorrect ou expiré` | Le PIN expire en quelques minutes → relancez le script |
| `Token invalide ou expiré` | Supprimez `ACCESS_TOKEN` du `.env` et relancez |
| Rate limit atteint | Augmentez le délai entre les posts |

---

## 📝 Fichiers
- `twitter_bot.py` : Script principal
- `.env` : Configuration (clés API et tokens)
- `README.md` : Ce fichier

---

## 📌 Sécurité
⚠️ **N'uploadez JAMAIS votre `.env` sur GitHub ou internet !**

Gardez-le local. Les clés API dedans donnent accès complet à votre compte Twitter.

---

## 🎯 Cas d'usage
- 📈 Augmenter l'engagement sur des tweets
- 🔗 Commenter automatiquement des trends
- 💼 Participations massives sans spam (avec délai)
- 🧪 Tester l'API Twitter

---

Bon twitting ! 🚀
