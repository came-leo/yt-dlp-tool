from urllib.parse import urlparse, parse_qs


def contient_playlist(url):
	# Détermine si l'URL contient un identifiant de playlist

	parametres = parse_qs(
		urlparse(url).query
	)

	return "list" in parametres