# 🎬 Guide de Création du Teaser Vidéo - AutoImport by VPWhite

## 📋 Ce dont vous avez besoin

### Logiciels recommandés (gratuits)
- **OBS Studio** (enregistrement d'écran) : https://obsproject.com/
- **DaVinci Resolve** (montage vidéo) : https://www.blackmagicdesign.com/products/davinciresolve
- **Canva** (graphiques et titres) : https://www.canva.com/

Ou alternatives plus simples :
- **Loom** : https://www.loom.com/
- **ScreenToGif** : https://www.screentogif.com/

---

## 🚀 Méthode 1 : Script Automatisé (Recommandé)

### Étapes :

1. **Préparer l'environnement**
   ```bash
   cd /app
   pip install playwright
   playwright install chromium
   ```

2. **Configurer le script**
   - Ouvrez `demo_script.py`
   - Modifiez `DEMO_SPEED` selon votre préférence : `"slow"`, `"medium"`, ou `"fast"`
   - Si vous avez des credentials de démo, décommentez la section appropriée

3. **Lancer l'enregistrement**
   - Ouvrez **OBS Studio**
   - Configurez la capture d'écran (Fenêtre ou Écran complet)
   - Cliquez sur "Démarrer l'enregistrement"
   - Dans un terminal : `python demo_script.py`
   - Attendez la fin du script
   - Arrêtez l'enregistrement dans OBS

4. **Résultat**
   - Vidéo brute : dans OBS (défaut : `~/Videos/`)
   - Screenshots : dans `demo_screenshots/`
   - Vidéo Playwright : dans `demo_videos/`

---

## 📸 Méthode 2 : Captures d'écran rapides

Si vous voulez juste des images statiques :

```bash
cd /app
python quick_screenshots.py
```

Résultat : captures dans le dossier `screenshots/`

---

## 🎨 Méthode 3 : Enregistrement Manuel (Plus flexible)

### Étapes :

1. **Préparer vos données de test**
   - Fichier Excel valide
   - Fichier Excel avec erreurs
   - Credentials Legisway de démo

2. **Lancer OBS Studio**
   - Source : Capture de fenêtre (Chrome/Edge)
   - Résolution : 1920x1080
   - FPS : 30 ou 60

3. **Scénario de démo** (3-5 minutes max)

   **INTRO (10 secondes)**
   - Logo + Titre : "AutoImport by VPWhite"
   - Sous-titre : "Automatisez vos imports dans Legisway"

   **PARTIE 1 : Connexion (20 secondes)**
   - Montrer le formulaire
   - Remplir les champs (flou sur les credentials)
   - Cliquer sur "Commencer"

   **PARTIE 2 : Configuration (30 secondes)**
   - Affichage des formats d'import
   - Sélection d'un format
   - **HIGHLIGHT** : Affichage automatique des listes de référence
   - Montrer les valeurs autorisées

   **PARTIE 3 : Validation (40 secondes)**
   - Upload d'un fichier avec erreurs
   - **HIGHLIGHT** : Affichage des erreurs détaillées
   - Correction du fichier
   - Re-upload

   **PARTIE 4 : Import (40 secondes)**
   - Validation réussie
   - **HIGHLIGHT** : Import automatique en mode rollback
   - Barre de progression
   - Fichier de résultat téléchargeable

   **OUTRO (10 secondes)**
   - Récapitulatif des fonctionnalités
   - Call-to-action

4. **Arrêter l'enregistrement**

---

## 🎬 Post-Production

### Montage vidéo (DaVinci Resolve ou équivalent)

1. **Importez votre vidéo**

2. **Ajoutez des éléments**
   - **Intro** : Écran titre (3-5 secondes)
   - **Transitions** : Douces entre chaque partie
   - **Annotations** : Flèches et textes pour expliquer
   - **Musique** : Fond musical moderne (sites gratuits : Bensound, Incompetech)

3. **Highlights à ajouter**
   ```
   ✨ "Récupération automatique des listes de référence"
   ✅ "Validation intelligente en temps réel"
   🔄 "Correction itérative facile"
   🚀 "Import automatique avec rollback"
   📊 "Rapport détaillé des erreurs"
   ```

4. **Textes à afficher**
   - Durée : 2-3 secondes par texte
   - Police : Moderne et lisible (Montserrat, Roboto)
   - Couleurs : Cohérentes avec l'application (violet/bleu)

5. **Exportez**
   - Format : MP4
   - Résolution : 1080p
   - Codec : H.264
   - Durée idéale : 2-3 minutes max

---

## 🎯 Structure de Teaser Recommandée

### Version Courte (30 secondes)
```
0-5s   : Logo + Titre
5-10s  : Problème : "Importer des données dans Legisway est fastidieux"
10-20s : Solution : Montage rapide des fonctionnalités clés
20-25s : Bénéfices : "Gagnez du temps, évitez les erreurs"
25-30s : Call-to-action
```

### Version Longue (2 minutes)
```
0-10s   : Intro
10-30s  : Démo connexion et formats
30-60s  : Démo validation (avec erreurs)
60-90s  : Démo import et résultat
90-110s : Récapitulatif des bénéfices
110-120s: Call-to-action
```

---

## 💡 Conseils Pro

### DO ✅
- Utilisez un fichier de test avec des données réalistes
- Montrez les erreurs ET les succès
- Mettez en avant les gains de temps
- Utilisez des annotations claires
- Gardez un rythme dynamique
- Ajoutez de la musique d'ambiance

### DON'T ❌
- Ne montrez pas les vraies credentials
- N'allez pas trop vite (laissez respirer)
- Ne mettez pas de musique trop forte
- N'oubliez pas le call-to-action
- Ne dépassez pas 3 minutes

---

## 🎵 Musiques gratuites recommandées

- **Bensound** : https://www.bensound.com/
- **Incompetech** : https://incompetech.com/
- **YouTube Audio Library** : Dans YouTube Studio
- **Pixabay Music** : https://pixabay.com/music/

Genres recommandés : Corporate, Tech, Upbeat

---

## 📤 Distribution

Une fois votre teaser terminé :

1. **YouTube** : Description + tags SEO
2. **LinkedIn** : Post avec description
3. **Site web** : Page d'accueil
4. **Email** : Campagne marketing

---

## 🆘 Besoin d'aide ?

Si vous avez besoin de :
- Captures d'écran spécifiques
- Modifications du script
- Conseils de montage

N'hésitez pas à demander !

---

**Bonne création ! 🎬✨**
