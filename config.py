import os

DOSSIER_PROJET = os.path.dirname(__file__)

COOKIES_PATH = os.path.join(
	DOSSIER_PROJET,
	"cookies.txt"
)

DOSSIER_TELECHARGEMENTS = os.path.join(
	DOSSIER_PROJET,
	"download"
)

os.makedirs(
	DOSSIER_TELECHARGEMENTS,
	exist_ok=True
)