def valider_qualite(valeur):
	# Vérifie que la qualité demander est autorisée

	qualites = [480, 720, 1080, 1440, 2160]

	valeur = int(valeur)

	if valeur not in qualites:
		raise ValueError(
			"La qualité doit être 480, 720, 1080, 1440 ou 2160"
		)

	return valeur