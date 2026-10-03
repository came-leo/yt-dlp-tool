import os
import subprocess

from config import COOKIES_PATH

def creer_commande(url, options, dossier_sortie, modele_sortie):
	# construit la commande yt-dlp sans l'exécuter

	commande = [
		"yt-dlp",
		*options,
		"-o",
		os.path.join(dossier_sortie, modele_sortie),
		url
	]

	if os.path.exists(COOKIES_PATH):
		commande.extend([
			"--coockie",
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