import sys

from config import DOSSIER_TELECHARGEMENT

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

from download import telecharger


def mode_interactif():
	# Lance le mode interactif

	dossier_sortie = DOSSIER_TELECHARGEMENT

	while True:
		afficher_entete()

		url, changement_dossier = demander_url(dossier_sortie)

		if changement_dossier:
			dossier_sortie = demander_dossier()
			continue

		return url, dossier_sortie


def mode_partage(url):
	# Lance le mode utilisé depuis une autre application

	dossier_sortie = DOSSIER_TELECHARGEMENT

	lancer_telechargement(
		url,
		dossier_sortie,
		"partage"
	)


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


def lancer_telechargement(url, dossier_sortie, mode="interactif"):
	# Prépare et lance le téléchargement

	choix = preparer_telechargement(url, dossier_sortie)

	telecharger(choix)

	if mode == "partage":
		print()
		input("Entrer pour quitter : ")
		return False

	print()
	choix = input(
		"Entrer pour quitter, (R) pour retourner au menu principal : "
	)

	return choix.lower() == "r"


def main():
	# Récupère les arguments fournis au lancement

	if len(sys.argv) > 1:
		mode_partage(sys.argv[1])
	else:
		while True:
			url, dossier_sortie = mode_interactif()

			retour_menu = lancer_telechargement(
				url,
				dossier_sortie
			)

			if not retour_menu:
				break


if __name__ == "__main__":
	main()