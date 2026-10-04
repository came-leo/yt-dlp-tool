import os

DOSSIER_PROJET = os.path.dirname(__file__)

COOKIES_PATH = os.path.join(
	DOSSIER_PROJET,
	"cookies.txt"
)

DOSSIER_TELECHARGEMENT = os.path.join(
	DOSSIER_PROJET,
	"download"
)

os.makedirs(
	DOSSIER_TELECHARGEMENT,
	exist_ok=True
)