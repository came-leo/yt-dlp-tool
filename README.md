# YT-DLP-TOOL

Outil Python interactif pour télécharger des vidéos, audios et playlists YouTube, TikTok, Facebook et autre
sous Windows, Linux et Android (via Termux) grace à yt-dlp

## 1. Prérequis

- Python 3.
- `yt-dlp`, pour récupérer les médias.
- `FFmpeg`, pour assembler certaines vidéos et convertir les fichiers audio en MP3.
- Node.js, utilisé par yt-dlp pour certains défis JavaScript de YouTube.
- `CustomTkinter`, nécessaire uniquement à l'interface graphique.

Installer les dépendances Python depuis le dossier du projet :

```bash
python -m pip install yt-dlp customtkinter
```

FFmpeg et Node.js s'installent séparément. Pour que yt-dlp les trouve, leurs exécutables doivent être accessibles depuis le `PATH`.

## 2. Lancement

Dans le dossier du projet, choisir l'une des deux interfaces :

- Interface graphique :

```bash
python gui.py
```

- Interface en terminal :

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

Dans le menu principal de l'interface en terminal :
- `c` : modifier le dossier de destination.
- `u` : mettre à jour yt-dlp.
- `q` : quitter le programme.

Dans l'interface en terminal, les options de playlist sont proposées lorsque l'URL contient un paramètre `list` (comme dans un lien de playlist YouTube). La prise en charge des playlists dépend également de la plateforme source.

## 5. Destination des fichiers

Les fichiers sont enregistrés dans le dossier de téléchargement configuré dans `settings.json`.

## 6. Limites

La qualité disponible dépend des formats fournis par la plateforme source. Certains téléchargements peuvent nécessiter une mise à jour de yt-dlp.

## 7. Créer le dossier Windows prêt à lancer

Depuis Windows, installer les dépendances de construction :

```powershell
python -m pip install -r requirements-build.txt
```

Vérifier que `yt-dlp.exe`, `ffmpeg.exe` et `ffprobe.exe` sont accessibles depuis le `PATH`, puis lancer :

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

Le dossier créé est `dist\yt-dlp-tool`. Lancer `yt-dlp-tool.exe` à l'intérieur. Le paquet inclut yt-dlp et FFmpeg ; Node.js reste une installation séparée.

**Projet :** `yt-dlp-tool`  
**Technologie principale :** Python et yt-dlp
