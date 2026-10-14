import os


def creer_commande(
	url,
	format_choisi,
	qualite,
	playlist,
	selection,
	dossier
):
	# Option de base
	commande = [
		"yt-dlp",
		"--ignore-config",
		"--js-runtimes", "node"
	]

	# Choix du format
	if format_choisi == "mp3":
		commande.extend(["-x", "--audio-format", "mp3"])
		modele = "%(title).80s.%(ext)s"
	else:
		limite = qualite if format_choisi == "qualite" else 720

		format_video = (
			f"bestvideo[height<=?{limite}]+bestaudio/"
			f"best[height<=?{limite}]/best"
		)

		commande.extend([
			"-f", format_video,
			"--merge-output-format", "mp4",
		])

		modele = "%(title).80s_%(height)sp.%(ext)s"

	# Gestion de la playlist
	if playlist == "unique":
		commande.append("--no-playlist")
	elif playlist == "complete":
		commande.append("--yes-playlist")
	elif playlist == "custom":
		commande.extend([
			"--yes-playlist",
			"--playlist-items", selection
		])

	# Dossier et nom des fichiers
	commande.extend([
		"-o", os.path.join(dossier, modele),
		url
	])

	return commande