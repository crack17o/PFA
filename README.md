# UniMate

Application web universitaire développée avec Flask.

## Fonctionnalités principales
- Gestion des rôles : Étudiant, Professeur/Assistant, Admin faculté, Superadmin
- Authentification sécurisée (email, mot de passe, OTP, 2FA optionnelle)
- Gestion des cours, promotions, départements, années académiques, semestres
- Dashboard par rôle
- Chatbot académique (API OpenAI)
- Gestion des livres
- Envoi d'emails
- Tests unitaires

# 🎓 Projet de Fin d’Année – UniMate

Bienvenue ! Ce dépôt a été généré automatiquement via GitHub Classroom pour la remise de votre projet de fin d’année individuel.

**Département** : Génie Informatique  
**Filière** : Ingénierie Logicielle  
**Année académique** : 2024–2025  
**Encadrant** : La Commission

---

## 📌 Objectif du projet
Ce projet a pour but de développer une application web universitaire moderne permettant la gestion des utilisateurs, cours, promotions, départements et facultés, avec une interface d’administration sécurisée et multi-rôles.

---

## 🛠️ Technologies utilisées
- **Langage principal** : Python, JavaScript
- **Framework** : Flask (backend), HTML/CSS + Bootstrap (frontend)
- **Base de données** : MySQL
- **Outils** : GitHub, Docker, Figma

---

## 🚀 Etapes pour lancer le projet
⚠️ À compléter obligatoirement. Exemple :

1. **Cloner ce dépôt :**
   ```sh
   git clone https://github.com/criagi-upc/projet-final-l3-crack17o.git
   cd nom-du-repo
   ```
2. **Créer un environnement virtuel (Python) :**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/Mac
   ```
3. **Installer les dépendances :**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configurer la base de données** (MySQL) et les variables d’environnement (voir `.env.example`)
5. **Lancer le serveur :**
   ```sh
   flask run
   ```

---

## 📁 Structure du projet

```
📦 nom-du-repo
 ┣ 📂 app/                  # Code source principal du projet (Flask)
 ┣ 📂 docs/                 # Documentation
 ┃ ┗ 📄 cahier-de-charge.pdf  # Cahier des charges au format PDF
 ┣ 📄 README.md             # Présentation du projet
 ┗ 📄 .gitignore            # Fichier gitignore
```

---

## 🎥 Démonstration
Lien vers la démonstration vidéo : 👉 https://youtu.be/votre-video-demo

---

## 🔁 Vous avez déjà commencé votre projet ailleurs ?
Si vous avez déjà un projet sur GitHub (dans votre compte personnel), vous n’avez pas besoin de le recommencer. Vous pouvez continuer à travailler dessus et simplement pousser le même code vers le dépôt de CRIAGI.

Pas de panique ! Voici comment transférer votre code existant dans ce dépôt :

### ✅ Étapes à suivre (une seule fois)
1. 📥 Acceptez l’invitation GitHub Classroom  
   Exemple : https://classroom.github.com/a/xxxxxxxx → Un dépôt sera automatiquement créé pour vous dans l’organisation de CRIAGI (ex: https://github.com/criagi-upc/projet-final-etudiant.git)
2. 🔗 Copiez le lien du dépôt Classroom généré
   - Cliquez sur le bouton “Code” dans GitHub
   - Copiez l’URL HTTPS du dépôt créé (ex: https://github.com/criagi-upc/projet-final-etudiant.git)
3. 🧠 Dans votre projet existant (sur votre machine) Ouvrez un terminal et placez-vous dans le dossier :
   ```sh
   cd mon-projet
   ```
4. ➕ Ajoutez le dépôt de CRIAGI comme destination secondaire (remote)
   ```sh
   git remote add criagi https://github.com/criagi-upc/projet-final-etudiant.git
   git fetch criagi
   git merge criagi/main --allow-unrelated-histories
   ```

### 🚀 Pour soumettre votre projet
À chaque fois que vous souhaitez soumettre votre travail à l’université :
```sh
git push criagi main
```
Et pour continuer à sauvegarder sur votre dépôt personnel habituel :
```sh
git push origin main
```

### ⚠️ Une autre étape à suivre (une seule fois) — Cette étape est optionnelle mais recommandée
Créez un remote "both" pour tout pousser d’un coup

Dans votre terminal, toujours dans le dossier du projet :
```sh
git remote add both https://github.com/votre-utilisateur/mon-projet.git
git remote set-url --add both https://github.com/criagi-upc/projet-final-etudiant.git
```
✅ Vous pouvez maintenant soumettre votre travail aux deux dépôts en même temps avec :
```sh
git push both main
```

---

## Résumé des commandes possibles
| Commande              | Effet                                         |
|----------------------|-----------------------------------------------|
| git push origin main  | 🔐 Sauvegarde dans votre dépôt personnel      |
| git push criagi main  | 🎓 Soumission officielle à CRIAGI             |
| git push both main    | ✅ Soumet dans les deux dépôts en une commande|

---

## Conditions
Pour que votre projet soit pris en compte, merci de suivre scrupuleusement toutes les étapes décrites dans ce README.

- Assurez-vous d’avoir accepté l’invitation GitHub Classroom avant de commencer.
- Copiez et ajoutez correctement le dépôt CRIAGI comme remote secondaire (criagi ou both).
- Poussez votre code dans le dépôt CRIAGI avant la date limite.
- Vérifiez que vos dernières modifications sont bien visibles sur GitHub.
- Tout dépôt non soumis conformément à ces consignes ne sera pas pris en compte.
- En cas de difficulté, contactez la COMMISSION avant la deadline.

---

## 💡 Comprendre Git et GitHub
Cette vidéo vous explique les bases de Git et GitHub : création de dépôt, commits, push/pull, branches, etc.  
Utile pour bien démarrer avec le versioning collaboratif.

👉 Regarder la vidéo sur YouTube

---

## 📄 Licence
Projet académique – Usage Strictement Pédagogique. © 2025 – Université Protestante au Congo - CRIAGI

---

About
l3-2024-2025-projet-final-template-project created by GitHub Classroom

Resources
- Readme
- Activity
- Custom properties

Stars: 0 stars
Watchers: 0 watching
Forks: 0 forks
Releases: No releases published
Packages: No packages published
