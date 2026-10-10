
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import subprocess


# Chemins du projet

DOSSIER_PROJET = os.path.dirname(
	os.path.abspath(__file__)
)

DOSSIER_DEFAUT = os.path.join(
	DOSSIER_PROJET,
	"download"
)

FICHIER_PARAMETRES = os.path.join(
	DOSSIER_PROJET,
	"settings.json"
)

FICHIER_COOKIES = os.path.join(
	DOSSIER_PROJET,
	"cookies.txt"
)


def charger_dossier():
	# Récupère le dernier dossier enregistré

	if os.path.isfile(FICHIER_PARAMETRES):
		try:
			with open(
				FICHIER_PARAMETRES,
				"r",
				encoding="utf-8"
			) as fichier:
				parametres = json.load(fichier)

			dossier = parametres.get(
				"dossier_telechargement"
			)

			if isinstance(dossier, str) and dossier.strip():
				dossier = os.path.abspath(
					os.path.expanduser(dossier)
				)

				os.makedirs(dossier, exist_ok=True)
				return dossier

		except (OSError, json.JSONDecodeError):
			pass

	os.makedirs(DOSSIER_DEFAUT, exist_ok=True)
	return DOSSIER_DEFAUT


def enregistrer_dossier(dossier):
	# Crée le dossier et mémorise son chemin

	dossier = os.path.abspath(
		os.path.expanduser(dossier)
	)

	os.makedirs(dossier, exist_ok=True)

	with open(
		FICHIER_PARAMETRES,
		"w",
		encoding="utf-8"
	) as fichier:
		json.dump(
			{"dossier_telechargement": dossier},
			fichier,
			indent=4
		)

	return dossier



def demander_url(dossier, url_partagee=None):
	# Demande l'URL ou permet de changer de dossier

	while True:
		print()
		print("YT-DLP-TOOL")
		print(f"Destination : {dossier}")
		print("[c] Dossier   [q] Quitter")
		print()

		if url_partagee is not None:
		    url = url_partagee.strip()
		    url_partagee = None
		else:
		    url = input("URL : ").strip()

		if url.lower() == "q":
			return None, dossier

		if url.lower() == "c":
			nouveau_dossier = input(
				"Nouveau dossier : "
			).strip()

			if nouveau_dossier:
				try:
					dossier = enregistrer_dossier(
						nouveau_dossier
					)
					print("Dossier enregistré :", dossier)

				except OSError as erreur:
					print("Erreur :", erreur)
			else:
				print("Dossier inchangé.")

			continue

		if url:
			return url, dossier

		print("Veuillez entrer une URL.")



def demander_format():
	# Demande le format de téléchargement

	print()
	print("FORMAT")
	print("1  MP3")
	print("2  Vidéo (720p maximum)")
	print("3  Qualité spécifique")

	while True:
		choix = input("Format : ").strip()

		if choix == "1":
			return "mp3"

		if choix == "2":
			return "video"

		if choix == "3":
			return "qualite"

		print("Choix invalide.")


def demander_qualite():
	# Demande la qualité vidéo

	qualites = {
		"1": 480,
		"2": 720,
		"3": 1080,
		"4": 1440,
		"5": 2160
	}

	print()
	print("QUALITÉ")
	print("1  480p")
	print("2  720p")
	print("3  1080p")
	print("4  1440p (2K)")
	print("5  2160p (4K)")

	while True:
		choix = input("Qualité : ").strip()

		if choix in qualites:
			return qualites[choix]

		print("Choix invalide.")


def contient_playlist(url):
	# Vérifie si l'URL contient un paramètre de playlist

	parametres = parse_qs(urlparse(url).query)
	return "list" in parametres


def demander_playlist():
	# Demande comment traiter la playlist

	print()
	print("PLAYLIST")
	print("1  Un seul élément")
	print("2  Toute la playlist")
	print("3  Sélection personnalisée")

	while True:
		choix = input("Choix : ").strip()

		if choix == "1":
			return "unique", None

		if choix == "2":
			return "complete", None

		if choix == "3":
			selection = input(
				"Éléments (ex. 1,2,3-5) : "
			).strip()

			if selection:
				return "custom", selection

		print("Choix invalide.")



def creer_commande(url, format_choisi, qualite, playlist, selection, dossier):
    # Options de base
    commande = [
        "yt-dlp",
        "--ignore-config",
        "--js-runtimes", "node",
    ]

    # Gestion des cookies


    # Choix du format
    if format_choisi == "mp3":
        commande.extend(["-x", "--audio-format", "mp3"])
        modele = "%(title)s.%(ext)s"

    
    else:
        limite = qualite if format_choisi == "qualite" else 720

        format_video = (
            f"bestvideo[height<={limite}][protocol=https][ext=mp4]+"
            f"bestaudio[protocol=https][ext=m4a]/"
            f"best[height<={limite}][protocol=https][ext=mp4]"
        )

        commande.extend([
            "-f", format_video,
            "--merge-output-format", "mp4",
        ])

        modele = "%(title)s_%(height)sp.%(ext)s"


    # Gestion de la playlist
    if playlist == "unique":
        commande.append("--no-playlist")
    elif playlist == "complete":
        commande.append("--yes-playlist")
    elif playlist == "custom":
        commande.extend(["--yes-playlist", "--playlist-items", selection])

    # Dossier et nom des fichiers
    commande.extend([
        "-o", os.path.join(dossier, modele),
        url,
    ])

    return commande




if __name__ == "__main__":
    dossier = charger_dossier()

    url_partagee = sys.argv[1] if len(sys.argv) > 1 else None

    while True:
        url, dossier = demander_url(dossier, url_partagee)
        url_partagee=None

        if url is None:
            print("Au revoir.")
            break

        format_choisi = demander_format()
        qualite = None

        if format_choisi == "qualite":
            qualite = demander_qualite()

        playlist = "unique"
        selection = None

        if contient_playlist(url):
            playlist, selection = demander_playlist()

        commande = creer_commande(
            url,
            format_choisi,
            qualite,
            playlist,
            selection,
            dossier
        )

        print()
        print("DÉMARRAGE DU TÉLÉCHARGEMENT")

        resultat = subprocess.run(commande)

        print()
        if resultat.returncode == 0:
            print("Téléchargement terminé.")
        else:
            print(
                f"Échec du téléchargement "
                f"(code {resultat.returncode})."
            )

        input("\nAppuie sur Entrée pour continuer...")
