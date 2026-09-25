#!/data/data/com.termux/files/usr/bin/bash

echo "Vérification de FFmpeg..."

if command -v ffmpeg >/dev/null 2>&1; then
	echo "FFmpeg est déjà installé."
else
	echo "Installation des dépendences..."
	pkg install -y ffmpeg
fi

echo "Installation des dépendences Python..."
pip install -r requirements.txt

echo "Installation terminée."