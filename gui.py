import tkinter as tk
from tkinter import ttk, filedialog
from main import charger_dossier, enregistrer_dossier
from downloader import creer_commande
import subprocess
import threading


class YtDlpToolApp:
	def __init__(self, root):
		self.root = root
		self.root.title("yt-dlp-tool")
		self.root.geometry("620x520")
		self.root.minsize(540, 460)

		self.dossier = tk.StringVar(
			value=charger_dossier()
		)
		self.url = tk.StringVar()
		self.format_choisi = tk.StringVar(value="video")
		self.qualite = tk.StringVar(value="720p")
		self.statut = tk.StringVar(value="Prêt")

		self.creer_interface()

	def creer_interface(self):
		# Style général
		style = ttk.Style()

		if "clam" in style.theme_names():
			style.theme_use("clam")

		style.configure(
			"Subtitle.TLabel",
			font=("Segoe UI", 20, "bold")
		)

		style.configure(
			"Subtitle.TLabel",
			font=("Segoe UI", 10)
		)

		style.configure(
			"Accent.TButton",
			font=("Segoe UI", 10, "bold"),
			padding=10
		)

		# Conteneur principal
		principal = ttk.Frame(self.root, padding=24)
		principal.pack(fill="both", expand=True)

		# En-tête
		ttk.Label(
			principal,
			text="yt-dlp-tool",
			style="Title.TLabel"
		).pack(anchor="w")

		ttk.Label(
			principal,
			text="Téléchargeur vidéo et audio",
			style="Subtitle.TLabel"
		).pack(anchor="w", pady=(2, 24))

		# URL
		ttk.Label(
			principal,
			text="URL de la vidéo ou de la playlist"
		).pack(anchor="w")

		self.champ_url = ttk.Entry(
			principal,
			textvariable=self.url
		)
		self.champ_url.pack(fill="x", pady=(6, 18))

		# Format
		ttk.Label(
			principal,
			text="Format"
		).pack(anchor="w")

		formats = ttk.Frame(principal)
		formats.pack(fill="x", pady=(6, 18))

		ttk.Radiobutton(
			formats,
			text="Vidéo MP4",
			variable=self.format_choisi,
			value="video",
			command=self.actualiser_qualite
		).pack(side="left", padx=(0, 20))

		ttk.Radiobutton(
			formats,
			text="Audio MP3",
			variable=self.format_choisi,
			value="mp3",
			command=self.actualiser_qualite
		).pack(side="left")

		# Qualité
		ttk.Label(
			principal,
			text="Qualité vidéo"
		).pack(anchor="w")

		self.list_qualite = ttk.Combobox(
			principal,
			textvariable=self.qualite,
			values=[
				"480p",
				"720p",
				"1080p",
				"1440p (2k)",
				"2160p (4k)"
			],
			state="readonly"
		)
		self.list_qualite.pack(
			fill="x",
			pady=(6, 18)
		)

		# Dossier de destination
		ttk.Label(
			principal,
			text="Dossier de destination"
		).pack(anchor="w")

		ligne_dossier = ttk.Frame(principal)
		ligne_dossier.pack(fill="x", pady=(6, 22))

		self.champ_dossier = ttk.Entry(
			ligne_dossier,
			textvariable=self.dossier,
			state="readonly"
		)
		self.champ_dossier.pack(
			side="left",
			fill="x",
			expand=True
		)

		ttk.Button(
			ligne_dossier,
			text="Parcourir...",
			command=self.choisir_dossier
		).pack(side="left", padx=(8, 0))

		# Bouton de téléchargement
		self.bouton_telecharger = ttk.Button(
			principal,
			text="Télécharger",
			style="Accent.TButton",
			command=self.telecharger
		)
		self.bouton_telecharger.pack(fill="x")

		# Statut
		ttk.Separator(
			principal,
			orient="horizontal"
		).pack(fill="x", pady=18)

		ttk.Label(
			principal,
			textvariable=self.statut
		).pack(anchor="w")

		self.actualiser_qualite()

	def choisir_dossier(self):
		dossier = filedialog.askdirectory(
			title="Choisir le dossier de destination",
			mustexist=True
		)

		if dossier:
			try:
				dossier = enregistrer_dossier(dossier)
				self.dossier.set(dossier)
				self.statut.set("Dossier enregistré.")
			except OSError as erreur:
				selt.statut.set(f"Erreur : {erreur}")

	def actualiser_qualite(self):
		if self.format_choisi.get() == "mp3":
			self.list_qualite.configure(state="disabled")
		else:
			self.list_qualite.configure(state="readonly")

	def telecharger(self):
		url = self.url.get().strip()
		dossier = self.dossier.get().strip()
		format_choisi = self.format_choisi.get()

		if not url:
			self.statut.set("Veuillez saisir une URL.")
			self.champ_url.focus_set()
			return


		if not dossier:
			self.statut.set("Veuillez choisir un dossier.")
			return

		qualite = None

		if format_choisi == "video":
			qualite = int(
				self.qualite.get().split("p")[0]
			)
			format_choisi = "qualite"

		commande = creer_commande(
			url,
			format_choisi,
			qualite,
			"unique",
			None,
			dossier
		)

		self.bouton_telecharger.configure(state="disabled")
		self.statut.set("Téléchargement en cours...")

		thread = threading.Thread(
			target=self.executer_telechargement,
			args=(commande,),
			daemon=True
		)
		thread.start()

	def executer_telechargement(self, commande):
		try:
			resultat = subprocess.run(
				commande,
				check=False
			)

			if resultat.returncode == 0:
				message = "Téléchargement terminé."
			else:
				message = (
					f"Echec du téléchargement "
					f"(code {resultat.returncode})"
				)

		except FileNotFoundError:
			message = (
				"Yt-dlp est introuvable. "
				"Vérifier son installation."
			)

		except OSError as erreur:
			message = f"Erreur system : {erreur}"

		self.root.after(
			0,
			self.terminer_telechargement,
			message
		)

	def terminer_telechargement(self, message):
		self.statut.set(message)
		self.bouton_telecharger.configure(state="normal")

def lancer_interface():
	root = tk.Tk()
	YtDlpToolApp(root)
	root.mainloop()


if __name__== "__main__":
	lancer_interface()