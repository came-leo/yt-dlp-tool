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

MODELE_VIDEO = "%(title)s_%(height)sp.%(ext)s"
MODELE_AUDIO = "%(title)s.%(ext)s"


def creer_commande(url, option_playlist, dossier_sortie, model_sortie):
	# Construit la commande yt-dlp sans l'exécuter
	
	commande = [
		"yt-dlp",
		option_playlist,
		"-o", os.path.join(dossier_sortie, model_sortie),
		url
	]

	if os.path.exists(cookies_path):
		commande.extend(["--cookies", cookies_path])

	return commande


def executer_commande(commande):
	# Exécute une commande yt-dlp et affiche son résultat

	print("▶ Téléchargement en cours...")

	resultat = subprocess.run(
		commande,
		stderr=subprocess.PIPE,
		text=True
	)

	if resultat.returncode == 0:
		print("✓ Téléchargement terminé")
	else:
		print(
			f"✗ Le téléchargement a échoué "
			f"(code {resultat.returncode})"
		)

		if resultat.stderr:
			print(resultat.stderr.strip())


def telecharger_video(url, option_playlist, dossier_sortie):
	commande = creer_commande(
		url,
		option_playlist,
		dossier_sortie,
		MODELE_VIDEO
	)

	executer_commande(commande)


def telecharger_qualite(url, option_playlist, qualite, dossier_sortie):
	commande = creer_commande(
		url,
		option_playlist,
		dossier_sortie,
		MODELE_VIDEO
	)

	commande.extend([
			"-f",
			f"bv*[height<={qualite}]+ba/b[height<={qualite}]"
		])

	executer_commande(commande)


def telecharger_audio(url, option_playlist, dossier_sortie):
	commande = creer_commande(
		url,
		option_playlist,
		dossier_sortie,
		MODELE_AUDIO
	)

	commande.extend([
			"-x",
			"--audio-format", "mp3",
			"--audio-quality", "0"
		])

	executer_commande(commande)


def valider_qualite(valeur):
	# Vérifie que la qualité demandée est autorisée
  
	qualites = [360, 480, 720, 1080]

	valeur = int(valeur)

	if valeur not in qualites:
		raise argparse.ArgumentTypeError(
			"La qualité doit être 360, 480, 720, ou 1080"
		)

	return valeur


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
	"--quality",
	type=valider_qualite,
	help="Qualité de la vidéo : 360, 480, 720 ou 1080"
)

parser.add_argument(
	"--output",
	default=dossier_telechargements,
	help="Dossier de téléchargement"
)


args = parser.parse_args()

dossier_sortie = args.output
os.makedirs(dossier_sortie, exist_ok=True)

if args.playlist:
	option_playlist = "--yes-playlist"
else:
	option_playlist = "--no-playlist"


if args.mp3:
	telecharger_audio(
		args.url,
		option_playlist,
		dossier_sortie
	)
elif args.quality is not None:
	telecharger_qualite(
		args.url,
		option_playlist,
		args.quality,
		dossier_sortie
	)
else:
	telecharger_video(
		args.url,
		option_playlist,
		dossier_sortie
	)