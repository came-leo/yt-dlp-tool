# YT-DLP-TOOL

Outil Python interactif pour télécharger des vidéos, audios et playlists YouTube, TikTok, Facebook et autre
sous Windows, Linux et Android (via Termux) grace à yt-dlp

## 1. Prérequis

- Python
- yt-dlp
- Node.js, pour les défis JavaScript de YouTube

## 2. Lancement

Dans le dossier du projet :

```bash
python main.py
```

## 3. Fonctionnalités

- Téléchargement de vidéos : 480p, 720p, 1080p, 1440p ou 2160p.
- Extraction audio au format MP3.
- Téléchargement de playlists complètes ou sélection de vidéos.
- Modification du dossier de destination.

## 4. Utilisation

1. Saisir l'URL YouTube.
2. Choisir le format souhaité.
3. Sélectionner la qualité vidéo ou les éléments de la playlist, si nécessaire.
4. Attendre la fin du téléchargement.

Dans le menu principal :
- `c` : modifier le dossier de destination.
- `q` : quitter le programme.

## 5. Destination des fichiers

Les fichiers sont enregistrés dans le dossier de téléchargement configuré dans `settings.json`.

## 6. Limites

La qualité disponible dépend des formats fournis par la plateforme source. Certains téléchargements peuvent nécessiter une mise à jour de yt-dlp.

**Projet :** `yt-dlp-tool`  
**Technologie principale :** Python et yt-dlp