import re
from urllib.parse import urlparse

def valider_qualite(valeur):
	# Vérifie que la qualité demandée est autorisée

	qualites = [480, 720, 1080, 1440, 2160]

	valeur = int(valeur)

	if valeur not in qualites:
		raise ValueError(
			"La qualité doit être 480, 720, 1080, 1440 ou 2160"
		)

	return valeur


def valider_selection_playlist(valeur):
	# Vérifie le format de sélection d'une playlist

	valeur = valeur.replace(" ", "")

	if not re.fullmatch(r"\d+(,\d+|-\d+)*", valeur):
		raise ValueError(
			"Format invalide. Exemple : 1,2,3-5"
		)

	return valeur


def valider_url(url):
	# Vérifie que la valeur saisie est une URL

	url = url.strip()

	parametres = urlparse(url)

	if parametres.scheme not in ("http", "https") or not parametres.netloc:
		raise ValueError("URL invalide.")

	return url