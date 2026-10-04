import os
import subprocess

from config import COOKIES_PATH


def creer_options(choix):
	# Transforme les choix utilisateur en options yt-dlp

	options = []

	if choix["format"] == "mp3":
		options.extend([
			"-x",
			"--audio-format",
			"mp3"
		])

	elif choix["format"] == "video":
		options.extend([
			"-f",
			"bestvideo[height<=720][ext=mp4]+"
			"bestaudio[ext=m4a]/best[height<=720][ext=mp4]"
		])

	elif choix["format"] == "qualite":
		options.extend([
			"-f",
			f"bestvideo[height<={choix['qualite']}][ext=mp4]+"
			f"bestaudio[ext=m4a]/best[height<={choix['qualite']}][ext=mp4]"
		])


	if choix["playlist"] == "complete":
		options.append("--yes-playlist")

	elif choix["playlist"] == "custom":
		options.extend([
			"--yes-playlist",
			"--playlist-items",
			choix["selection"]
		])

	else:
		options.append("--no-playlist")

	return options


def choisir_modele_sortie(format_choisi):
	# Choisit le modèle de nom du fichier

	if format_choisi == "mp3":
		return "%(title)s.%(ext)s"
	return "%(title)s_%(height)sp.%(ext)s"


def creer_commande(url, options, dossier_sortie, modele_sortie):
	# construit la commande yt-dlp sans l'exécuter

	commande = [
		"yt-dlp",
		"--ignore-config",
		"--js-runtimes",
		"node",
		"--embed-thumbnail",
		*options,
		"-o",
		os.path.join(dossier_sortie, modele_sortie),
		url
	]

	if os.path.exists(COOKIES_PATH):
		commande.extend([
			"--cookies",
			COOKIES_PATH
		])

	return commande


def executer_commande(commande):
	# Exécute la commande yt-dlp et affiche le resultat

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


def telecharger(choix):
	# Construit et exécute la commande yt-dlp

	options = creer_options(choix)

	modele_sortie = choisir_modele_sortie(
		choix["format"]
	)

	commande = creer_commande(
		choix["url"],
		options,
		choix["dossier_sortie"],
		modele_sortie
	)

	executer_commande(commande)