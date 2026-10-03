import sys

from config import DOSSIER_TELECHARGEMENTS

from interface import (
	afficher_entete,
	demander_url,
	demander_dossier,
	choisir_format,
	choisir_qualite,
	choisir_type_playlist,
	demander_selection_playlist
)

from playlist import contient_playlist

from download import creer_commande, executer_commande


def mode_interactif():
	# Lance le mode interactif

	dossier_sortie = DOSSIER_TELECHARGEMENTS

	while True:
		afficher_entete()

		url, changement_dossier = demander_url(dossier_sortie)

		if changement_dossier:
			dossier_sortie = demander_dossier()
			continue

		return url, dossier_sortie


def mode_partage():
	# Lance le mode utilisé depuis une autre application

	print(f"URL reçue : {url}")


def preparer_telechargement(url, dossier_sortie):
	# Prépare les choix nécessaires au téléchargement

	playlist = contient_playlist(url)

	format_choisi = choisir_format(playlist)

	if format_choisi == "qualite":
		qualite = choisir_qualite()
	else:
		qualite = None

	if playlist:
		type_playlist = choisir_type_playlist()
	else:
		type_playlist = "unique"

	if type_playlist == "custom":
		selection = demander_selection_playlist()
	else:
		selection = None

	return {
		"url": url,
		"dossier_sortie": dossier_sortie,
		"format": format_choisi,
		"qualite": qualite,
		"playlist": type_playlist,
		"selection": selection
	}


def creer_options(choix):
	# Transforme les choix utilisateur en options yt-dlp

	options = []

	if choix["format"] == "mp3":
		options.extend([
			"-x",
			"--audio-format",
			"mp3"
		])

	elif choix["format"] == "qualite":
		options.extend([
			"-f",
			f"bestvideo[height<={choix['qualite']}]+"
			f"bestaudio/best[height<={choix['qualite']}]"
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


def main():
	# Récupère les arguments fournis au lancement

	if len(sys.argv) > 1:
		mode_partage(sys.argv[1])
	else:
		url, dossier_sortie = mode_interactif()

		choix = preparer_telechargement(url, dossier_sortie)

		options = creer_options(choix)

		if choix["format"] == "mp3":
			modele_sortie = "%(title)s.%(ext)s"
		else:
			modele_sortie = "%(title)s_%(height)sp.%(ext)s"

		commande = creer_commande(
			choix["url"],
			options,
			choix["dossier_sortie"],
			modele_sortie
		)

		executer_commande(commande)

		print(options)



if __name__ == "__main__":
	main()