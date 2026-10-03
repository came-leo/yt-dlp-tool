def afficher_entete():
	# Affiche l'entete principale de l'application

	print("YT-DLP-TOOL")
	print()
	print("Télécharger une vidéo, un mp3 ou une playlist avec yt-dlp")


def demander_url(dossier_sortie):
	# Demande l'url ou permet de changer le dossier

	print(f'Destination "{dossier_sortie}", taper (c) pour changer de dossier')
	print()

	url = input("URL : ")

	if url.lower() == "c":
		return	None, True

	return url, False


def demander_dossier():
	# Demande à l'utilisateur le nouveau dossier de téléchargement

	return input("Destination : ")


def choisir_format(contien_playlist):
	# Affiche le menu permettant de choisir le format

	if contien_playlist:
		print("L'URL est une vidéo et une playlist")
	else:
		print("L'URL est une vidéo")

	print()
	print("1. mp3")
	print("2. vidéo")
	print("3. qualité spécifique")
	print()

	choix = input("Choix : ")

	if choix == "1":
		return "mp3"

	if choix == "2":
		return "video"

	if choix == "3":
		return "qualite"

	return None


def choisir_qualite():
	# Affiche les qualités disponibles

	print()
	print("1. 480p")
	print("2. 720p")
	print("3. 1080p")
	print("4. 1440p (2k)")
	print("5. 2160p (4k)")
	print()

	choix = input("Choix : ")

	if choix == "1":
		return 480

	if choix == "2":
		return 720

	if choix == "3":
		return 1080

	if choix == "4":
		return 1440

	if choix == "5":
		return 2160

	
	return None


def choisir_type_playlist():
	# Demande comment traiter la playlist

	print()
	print("1. vidéo/audio unique")
	print("2. toute la playlist")
	print("3. playlist personalisée")
	print()

	choix = input("Choix : ")

	if choix == "1":
		return "unique"

	if choix == "2":
		return "complete"

	if choix == "3":
		return "custom"

	return None


def demander_selection_playlist():
	# Demande les éléments de la playlist à télécharger

	print()
	print("Exemple : 1,2,3-5")
	print()

	return input("Choix : ").replace(" ", "")