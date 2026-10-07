import sys

from config import DOSSIER_TELECHARGEMENT

from interface import (
	RETOUR,
	MENU,
	QUITTER,
	menu_principal,
	demander_dossier,
	menu_format,
	menu_qualite,
	menu_playlist,
	menu_selection
)

from playlist import contient_playlist
from validation import valider_url, valider_selection_playlist
from download import telecharger


def preparer_telechargement(url, dossier_sortie):
	# Parcourt les menus et prépare les choix du téléchargement

	playlist = contient_playlist(url)

	while True:
		format_choisi = menu_format(playlist)

		if format_choisi == QUITTER:
			return QUITTER

		if format_choisi == MENU:
			return MENU

		if format_choisi == RETOUR:
			return RETOUR

		qualite = None

		if format_choisi == "qualite":
			while True:
				qualite = menu_qualite()

				if qualite == QUITTER:
					return QUITTER

				if qualite == MENU:
					return MENU

				if qualite == RETOUR:
					break

				break

			if qualite == RETOUR:
				continue

		type_playlist = "unique"
		selection = None

		if playlist:
			while True:
				type_playlist = menu_playlist()

				if type_playlist == QUITTER:
					return QUITTER

				if type_playlist == MENU:
					return MENU

				if type_playlist == RETOUR:
					break

				break

			if type_playlist == RETOUR:
				continue

			if type_playlist == "custom":
				while True:
					selection = menu_selection()

					if selection == QUITTER:
						return QUITTER

					if selection == MENU:
						return MENU

					if selection == RETOUR:
						break

					try:
						selection = valider_selection_playlist(
							selection
						)
						break
					except ValueError as erreur:
						print(erreur)

				if selection == RETOUR:
					continue

		return {
			"url": url,
			"dossier_sortie": dossier_sortie,
			"format": format_choisi,
			"qualite": qualite,
			"playlist": type_playlist,
			"selection": selection
		}


def mode_interactif():
	# Gère le mode lancé directement depuis Termux

	dossier_sortie = DOSSIER_TELECHARGEMENT

	while True:
		choix = menu_principal(dossier_sortie)

		if choix == QUITTER:
			return QUITTER

		if choix == "changer_dossier":
			dossier_sortie = demander_dossier()
			continue

		try:
			url = valider_url(choix)
		except ValueError as erreur:
			print(erreur)
			input("Entrer pour continuer...")
			continue

		resultat = preparer_telechargement(
			url,
			dossier_sortie
		)

		if resultat == QUITTER:
			return QUITTER

		if resultat in (MENU, RETOUR):
			continue

		telecharger(resultat)

		print()
		print("✓ Téléchargement terminé")
		print()
		print("[q] Quitter")
		print("[m] Menu")
		print()

		choix = input("Choix : ").strip().lower()

		if choix == "q":
			return QUITTER

		if choix == "m":
			continue


def mode_partage(url):
	# Gère le mode lancé depuis le partage Android

	dossier_sortie = DOSSIER_TELECHARGEMENT

	try:
		url = valider_url(url)
	except ValueError as erreur:
		print(erreur)
		input("Entrer pour quitter...")
		return

	resultat = preparer_telechargement(
		url,
		dossier_sortie
	)

	if resultat in (QUITTER, MENU, RETOUR):
		return

	telecharger(resultat)

	print()
	input("Entrer pour quitter...")


def main():
	# Détermine le mode de lancement

	if len(sys.argv) > 1:
		mode_partage(sys.argv[1])
	else:
		mode_interactif()


if __name__ == "__main__":
	main()