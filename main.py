import os
import argparse
import subprocess


dossier_projet = os.path.dirname(__file__)

cookies_path = os.path.join(
	dossier_projet,
	"cookies.txt"
)

dossier_telechargements = os.path.join(
	dossier_projet,
	"downloads"
)

os.makedirs(dossier_telechargements, exist_ok=True)


def creer_commande(url, option_playlist):
	commande = [
		"yt-dlp",
		option_playlist,
		"-o", os.path.join(dossier_telechargements, "%(title)s.%(ext)s"),
		url
	]

	if os.path.exists(cookies_path):
		commande.extend(["--cookies", cookies_path])

	return commande


def executer_commande(commande):
	resultat = subprocess.run(commande)

	if resultat.returncode == 0:
		print("Téléchargement terminé")
	else:
		print(
			f"Le téléchargement a échoué "
			f"(code {resultat.returncode})"
		)


def telecharger_video(url, option_playlist):
	commande = creer_commande(url, option_playlist)

	executer_commande(commande)


def telecharger_1080p(url, option_playlist):
	commande = creer_commande(url, option_playlist)

	commande.extend([
			"-f",
			"bv*[height<=1080]+ba/b[height<=1080]"
		])

	executer_commande(commande)


def telecharger_audio(url, option_playlist):
	commande = creer_commande(url, option_playlist)

	commande.extend([
			"-x",
			"--audio-format", "mp3",
			"--audio-quality", "0"
		])

	executer_commande(commande)


parser = argparse.ArgumentParser(
	description="Télécharger une vidéo ou un MP3 avec yt-dlp."
)

parser.add_argument(
	"url",
	help="URL de la vidéo à télécharger"
)

parser.add_argument(
	"--playlist",
	action="store_true",
	help="Télécharger la playlist entière"
)

groupe_format = parser.add_mutually_exclusive_group()

groupe_format.add_argument(
	"--mp3",
	action="store_true",
	help="Télécharger uniquement l'audio en MP3"
)

groupe_format.add_argument(
	"--1080p",
	action="store_true",
	dest="quality_1080p",
	help="Télécharger la vidéo jusqu'en 1080p"
)

args = parser.parse_args()

if args.playlist:
	option_playlist = "--yes-playlist"
else:
	option_playlist = "--no-playlist"


if args.mp3:
	telecharger_audio(args.url, option_playlist)
elif args.quality_1080p:
	telecharger_1080p(args.url, option_playlist)
else:
	telecharger_video(args.url, option_playlist)