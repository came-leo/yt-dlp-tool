import unittest
from unittest.mock import Mock, patch

from gui import YtDlpToolApp


class TestArretTelechargement(unittest.TestCase):
	def creer_app(self, processus=None):
		app = YtDlpToolApp.__new__(YtDlpToolApp)
		app.processus = processus
		app.arret_demande = False
		app.bouton_telecharger = Mock()
		app.bouton_telecharger.cget.return_value = "disabled"
		app.bouton_arreter = Mock()
		app.statut = Mock()
		app.arreter_processus = Mock()
		return app

	def test_memorise_un_clic_avant_le_demarrage_du_processus(self):
		app = self.creer_app()

		app.arreter_telechargement()

		self.assertTrue(app.arret_demande)
		app.arreter_processus.assert_not_called()
		app.statut.set.assert_called_with("Arrêt du téléchargement...")

	def test_arrete_un_processus_deja_lance(self):
		processus = Mock()
		processus.poll.return_value = None
		app = self.creer_app(processus)

		app.arreter_telechargement()

		self.assertTrue(app.arret_demande)
		app.arreter_processus.assert_called_once_with(processus)

	def test_transmet_une_demande_precoce_au_processus_demarre(self):
		processus = Mock()
		processus.stdout = iter(())
		processus.wait.return_value = 1
		app = self.creer_app()
		app.arret_demande = True
		app.root = Mock()

		with patch("gui.subprocess.Popen", return_value=processus):
			app.executer_telechargement(["yt-dlp"])

		app.arreter_processus.assert_called_once_with(processus)
		self.assertEqual(
			app.root.after.call_args.args[-1],
			"Téléchargement arrêté.",
		)

if __name__ == "__main__":
	unittest.main()
