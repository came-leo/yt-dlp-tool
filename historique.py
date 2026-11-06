import os
import sqlite3

from main import DOSSIER_PARAMETRES


FICHIER_HISTORIQUE = os.path.join(
	DOSSIER_PARAMETRES,
	"historique.sqlite3"
)


def connecter():
	os.makedirs(DOSSIER_PARAMETRES, exist_ok=True)
	connexion = sqlite3.connect(FICHIER_HISTORIQUE)
	connexion.execute(
		"""
		CREATE TABLE IF NOT EXISTS telechargements (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			chemin TEXT NOT NULL UNIQUE,
			type TEXT NOT NULL,
			taille INTEGER NOT NULL,
			date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)
	connexion.commit()
	return connexion


def ajouter(chemin):
	chemin = os.path.abspath(chemin)
	if not os.path.isfile(chemin):
		return
	type_fichier = os.path.splitext(chemin)[1].lstrip(".").upper()
	connexion = connecter()
	try:
		connexion.execute(
			"""
			INSERT INTO telechargements (chemin, type, taille)
			VALUES (?, ?, ?)
			ON CONFLICT(chemin) DO UPDATE SET
				type = excluded.type,
				taille = excluded.taille,
				date = CURRENT_TIMESTAMP
			""",
			(chemin, type_fichier, os.path.getsize(chemin)),
		)
		connexion.commit()
	finally:
		connexion.close()


def lister():
	connexion = connecter()
	try:
		return connexion.execute(
			"SELECT id, chemin, type, taille, date "
			"FROM telechargements ORDER BY id DESC"
		).fetchall()
	finally:
		connexion.close()


def supprimer(identifiant):
	connexion = connecter()
	try:
		connexion.execute(
			"DELETE FROM telechargements WHERE id = ?",
			(identifiant,),
		)
		connexion.commit()
	finally:
		connexion.close()


def supprimer_tout():
	connexion = connecter()
	try:
		connexion.execute("DELETE FROM telechargements")
		connexion.commit()
	finally:
		connexion.close()
