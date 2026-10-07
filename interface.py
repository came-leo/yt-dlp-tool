import os


RETOUR = "retour"
MENU = "menu"
QUITTER = "quitter"


def lire_choix(message):
	# Lit une saisie et reconnaît les commandes de navigation

	choix = input(message).strip().lower()

	if choix == "r":
		return RETOUR

	if choix == "m":
		return MENU

	if choix == "q":
		return QUITTER

	return choix


def menu_principal(dossier_sortie):
	# Affiche le menu principal

	os.system("clear")

	print("=== YT-DLP-TOOL ===")
	print()
	print("Télécharger avec yt-dlp")
	print()
	print(f"Destination : {dossier_sortie}")
	print()
	print("[c] Changer de dossier    [q] Quitter")
	print()

	while True:
		choix = lire_choix("URL : ")

		if choix == QUITTER:
			return QUITTER

		if choix == "c":
			return "changer_dossier"

		if choix:
			return choix

		print("Veuillez entrer une URL.")


def demander_dossier():
	# Demande le nouveau dossier de téléchargement

	print()
	print("CHANGER DE DOSSIER")
	print()

	while True:
		dossier = input("Destination : ").strip()

		if dossier:
			os.makedirs(dossier, exist_ok=True)
			return dossier

		print("Veuillez entrer un dossier.")


def menu_format(contient_playlist):
	# Affiche le menu de choix du format

	os.system("clear")

	print("[r] Retour    [m] Menu    [q] Quitter")
	print()
	print("1  MP3")
	print("2  Vidéo")
	print("3  Qualité spécifique")
	print()

	while True:
		choix = lire_choix("Choix : ")

		if choix == RETOUR:
			return RETOUR

		if choix == MENU:
			return MENU

		if choix == QUITTER:
			return QUITTER

		if choix == "1":
			return "mp3"

		if choix == "2":
			return "video"

		if choix == "3":
			return "qualite"

		print("Choix invalide.")


def menu_qualite():
	# Affiche le menu de choix de la qualité vidéo

	print()
	print("1  480p")
	print("2  720p")
	print("3  1080p")
	print("4  1440p (2K)")
	print("5  2160p (4K)")
	print()

	qualites = {
		"1": 480,
		"2": 720,
		"3": 1080,
		"4": 1440,
		"5": 2160
	}

	while True:
		choix = lire_choix("Choix : ")

		if choix == RETOUR:
			return RETOUR

		if choix == MENU:
			return MENU

		if choix == QUITTER:
			return QUITTER

		if choix in qualites:
			return qualites[choix]

		print("Choix invalide.")


def menu_playlist():
	# Affiche le menu de traitement de la playlist

	print()
	print("1  Vidéo/audio unique")
	print("2  Toute la playlist")
	print("3  Sélection personnalisée")
	print()

	while True:
		choix = lire_choix("Choix : ")

		if choix == RETOUR:
			return RETOUR

		if choix == MENU:
			return MENU

		if choix == QUITTER:
			return QUITTER

		if choix == "1":
			return "unique"

		if choix == "2":
			return "complete"

		if choix == "3":
			return "custom"

		print("Choix invalide.")


def menu_selection():
	# Demande les éléments de la playlist à télécharger

	print()
	print("Exemple : 1,2,3-5")
	print()

	while True:
		choix = lire_choix("Sélection : ")

		if choix == RETOUR:
			return RETOUR

		if choix == MENU:
			return MENU

		if choix == QUITTER:
			return QUITTER

		if choix:
			return choix

		print("Veuillez entrer une sélection.")