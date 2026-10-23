import unittest

from downloader import creer_commande, selection_playlist_valide


class TestSelectionPlaylist(unittest.TestCase):
	def test_accepte_numeros_et_plages(self):
		self.assertTrue(selection_playlist_valide("1, 2, 3-5"))

	def test_refuse_selection_invalide(self):
		for selection in ("", "abc", "0", "5-2", "1,,2"):
			with self.subTest(selection=selection):
				self.assertFalse(selection_playlist_valide(selection))


class TestCreationCommande(unittest.TestCase):
	def test_construit_une_commande_video(self):
		commande = creer_commande(
			"https://example.com/video",
			"qualite",
			1080,
			"unique",
			None,
			"downloads",
		)

		self.assertIn("--no-playlist", commande)
		self.assertIn(
			"bestvideo[height<=?1080]+bestaudio/"
			"best[height<=?1080]/best",
			commande,
		)
		self.assertEqual(commande[-1], "https://example.com/video")

	def test_construit_une_commande_audio(self):
		commande = creer_commande(
			"https://example.com/audio",
			"mp3",
			None,
			"unique",
			None,
			"downloads",
		)

		self.assertIn("-x", commande)
		self.assertIn("--audio-format", commande)
		self.assertIn("mp3", commande)

	def test_ajoute_la_selection_personnalisee(self):
		commande = creer_commande(
			"https://example.com/playlist",
			"video",
			None,
			"custom",
			"1, 2, 3-5",
			"downloads",
		)

		self.assertIn("--yes-playlist", commande)
		index = commande.index("--playlist-items")
		self.assertEqual(commande[index + 1], "1, 2, 3-5")


if __name__ == "__main__":
	unittest.main()
