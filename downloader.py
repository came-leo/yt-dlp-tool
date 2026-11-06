import os
import shutil
import sys


def chemin_executable(nom):
	"""Trouve l'exécutable fourni avec l'application ou installé sur le système."""

	if getattr(sys, "frozen", False):
		dossier_application = os.path.dirname(sys.executable)
		nom_windows = f"{nom}.exe" if os.name == "nt" else nom
		chemin_inclus = os.path.join(
			dossier_application,
			"tools",
			nom_windows
		)

		if os.path.isfile(chemin_inclus):
			return chemin_inclus

	return shutil.which(nom) or nom


def selection_playlist_valide(selection):
	if not selection.strip():
		return False

	for element in selection.split(","):
		bornes = element.strip().split("-")
		if len(bornes) > 2:
			return False
		if not all(borne.isdigit() for borne in bornes):
			return False

		valeurs = [int(borne) for borne in bornes]
		if any(valeur < 1 for valeur in valeurs):
			return False
		if len(valeurs) == 2 and valeurs[0] > valeurs[1]:
			return False

	return True


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
		chemin_executable("yt-dlp"),
		"--ignore-config",
		"--newline",
		"--progress"
	]

	chemin_ffmpeg = chemin_executable("ffmpeg")
	if os.path.isabs(chemin_ffmpeg) and os.path.isfile(chemin_ffmpeg):
		commande.extend([
			"--ffmpeg-location",
			os.path.dirname(chemin_ffmpeg)
		])

	chemin_node = chemin_executable("node")
	if os.path.isabs(chemin_node) and os.path.isfile(chemin_node):
		commande.extend([
			"--js-runtimes",
			f"node:{chemin_node}"
		])

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


def creer_options_api(
	format_choisi,
	qualite,
	playlist,
	selection,
	dossier,
	progress_hook,
	post_hook,
):
	"""Prépare les options yt-dlp pour le téléchargement depuis l'interface."""
	options = {
		"ignoreconfig": True,
		"quiet": True,
		"no_warnings": True,
		"outtmpl": os.path.join(
			dossier,
			"%(title).80s.%(ext)s"
			if format_choisi == "mp3"
			else "%(title).80s_%(height)sp.%(ext)s",
		),
		"progress_hooks": [progress_hook],
		"post_hooks": [post_hook],
	}

	chemin_ffmpeg = chemin_executable("ffmpeg")
	if os.path.isabs(chemin_ffmpeg) and os.path.isfile(chemin_ffmpeg):
		options["ffmpeg_location"] = os.path.dirname(chemin_ffmpeg)

	chemin_node = chemin_executable("node")
	if os.path.isabs(chemin_node) and os.path.isfile(chemin_node):
		options["js_runtimes"] = {"node": {"path": chemin_node}}

	if format_choisi == "mp3":
		options["format"] = "bestaudio/best"
		options["postprocessors"] = [{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "mp3",
		}]
	else:
		limite = qualite if format_choisi == "qualite" else 720
		options["format"] = (
			f"bestvideo[height<=?{limite}]+bestaudio/"
			f"best[height<=?{limite}]/best"
		)
		options["merge_output_format"] = "mp4"

	if playlist == "unique":
		options["noplaylist"] = True
	elif playlist == "custom":
		options["playlist_items"] = selection

	return options
