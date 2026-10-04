import os
from validation import (
	valider_qualite,
	valider_selection_playlist,
	valider_url
)


def afficher_entete():
	# Affiche l'entete principale de l'application

	# Nettoie le terminal au lancement (linux)
	os.system("clear")

	print("YT-DLP-TOOL")
	print()
	print("Télécharger une vidéo, un mp3 ou une playlist avec yt-dlp")


def demander_url(dossier_sortie):
	# Demande l'url ou permet de changer le dossier

	print(f'Destination "{dossier_sortie}", taper (C) pour changer de dossier')
	print()

	while True:
		url = input("URL : ")

		if url.lower() == "c":
			return	None, True

		try:
			url = valider_url(url)
			return url, False
		except ValueError as erreur:
				print(erreur)

	


def demander_dossier():
	# Demande à l'utilisateur le nouveau dossier de téléchargement

	dossier = input("Destination : ")

	os.makedirs(dossier, exist_ok=True)

	return dossier


def choisir_format(contient_playlist):
	# Affiche le menu permettant de choisir le format

	print()
	if contient_playlist:
		print("L'URL est une vidéo et une playlist")
	else:
		print("L'URL est une vidéo")

	print()
	print("1. mp3")
	print("2. vidéo")
	print("3. qualité spécifique")
	print()

	while True:
		choix = input("Choix : ")

		if choix == "1":
			return "mp3"

		if choix == "2":
			return "video"

		if choix == "3":
			return "qualite"

		print("Choix invalide. Veuillez choisir 1, 2 ou 3.")


def choisir_qualite():
	# Affiche les qualités disponibles

	print()
	print("1. 480p")
	print("2. 720p")
	print("3. 1080p")
	print("4. 1440p (2k)")
	print("5. 2160p (4k)")
	print()

	while True:
		choix = input("Choix : ")

		qualites = {
			"1": 480,
			"2": 720,
			"3": 1080,
			"4": 1440,
			"5": 2160,
		}

		if choix in qualites:
			return valider_qualite(qualites[choix])

		print("Choix invalide. Veuillez choisir de 1 à 5.")


def choisir_type_playlist():
	# Demande comment traiter la playlist

	print()
	print("1. vidéo/audio unique")
	print("2. toute la playlist")
	print("3. playlist personnalisée")
	print()

	while True:
		choix = input("Choix : ")

		if choix == "1":
			return "unique"

		if choix == "2":
			return "complete"

		if choix == "3":
			return "custom"

		print("Choix invalide. Veuillez choisir 1, 2 ou 3.")


def demander_selection_playlist():
	# Demande les éléments de la playlist à télécharger

	print()
	print("Exemple : 1,2,3-5")
	print()

	while True:
		choix = input("Choix : ")

		try:
			return valider_selection_playlist(choix)
		except ValueError as erreur:
			print(erreur)