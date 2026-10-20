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
		self.root.geometry("620x740")
		self.root.minsize(540, 460)

		self.dossier = tk.StringVar(
			value=charger_dossier()
		)
		self.url = tk.StringVar()
		self.format_choisi = tk.StringVar(value="video")
		self.qualite = tk.StringVar(value="720p")
		self.playlist = tk.StringVar(value="unique")
		self.selection_playlist = tk.StringVar()
		self.statut = tk.StringVar(value="Prêt")
		self.progression = tk.DoubleVar(value=0)
		self.details_progression = tk.StringVar(
			value="En attente d'un téléchargement"
		)
		self.processus = None
		self.arret_demande = False
		self.taille_telechargee = tk.StringVar(value="Téléchargé : -")
		self.vitesse = tk.StringVar(value="Vitesse : -")
		self.temps_restant = tk.StringVar(value="Temps restant : -")

		self.creer_interface()

	def creer_interface(self):
		# Style général
		style = ttk.Style()

		if "clam" in style.theme_names():
			style.theme_use("clam")

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

		# Gestion de la playlist
		ttk.Label(
			principal,
			text="contenu à télécharger"
		).pack(anchor="w")

		cadre_playlist = ttk.Frame(principal)
		cadre_playlist.pack(fill="x", pady=(6, 10))

		ttk.Radiobutton(
			cadre_playlist,
			text="Un seul élément",
			variable=self.playlist,
			value="unique",
			command=self.actualiser_playlist
		).pack(anchor="w")

		ttk.Radiobutton(
			cadre_playlist,
			text="Toute la playlist",
			variable=self.playlist,
			value="complete",
			command=self.actualiser_playlist
		).pack(anchor="w")

		ttk.Radiobutton(
			cadre_playlist,
			text="Sélection personnalisée",
			variable=self.playlist,
			value="custom",
			command=self.actualiser_playlist
		).pack(anchor="w")

		self.champ_selection = ttk.Entry(
			principal,
			textvariable=self.selection_playlist,
			state="disabled"
		)
		self.champ_selection.pack(fill="x", pady=(0, 18))

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

		self.bouton_arreter = ttk.Button(
			principal,
			text="Arrêter",
			command=self.arreter_telechargement,
			state="disabled"
		)
		self.bouton_arreter.pack(fill="x", pady=(8, 0))


		# Statut
		ttk.Separator(
			principal,
			orient="horizontal"
		).pack(fill="x", pady=18)

		ttk.Label(
			principal,
			textvariable=self.statut
		).pack(anchor="w")

		# Barre de progression
		ttk.Progressbar(
			principal,
			variable=self.progression,
			maximum=100,
			mode="determinate",
		).pack(fill="x", pady=(12, 6))

		# Pourcentage et détails

		self.infos_progression = ttk.Label(
			principal,
			textvariable=self.details_progression
		)
		self.infos_progression.pack(anchor="w")

		# Taille, vitesse et temps restant
		ligne_infos = ttk.Frame(principal)
		ligne_infos.pack(fill="x", pady=(8, 0))

		ttk.Label(
			ligne_infos,
			textvariable=self.taille_telechargee
		).pack(side="left", expand=True, anchor="w")

		ttk.Label(
			ligne_infos,
			textvariable=self.vitesse
		).pack(side="left", expand=True, anchor="w")

		ttk.Label(
			ligne_infos,
			textvariable=self.temps_restant
		).pack(side="left", expand=True, anchor="w")

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
				self.statut.set(f"Erreur : {erreur}")

	def actualiser_qualite(self):
		if self.format_choisi.get() == "mp3":
			self.list_qualite.configure(state="disabled")
		else:
			self.list_qualite.configure(state="readonly")

	def actualiser_playlist(self):
		if self.playlist.get() == "custom":
			self.champ_selection.configure(state="normal")
		else:
			self.champ_selection.configure(state="disabled")
			self.selection_playlist.set("")

	def arreter_telechargement(self):
		processus = self.processus

		if processus is not None and processus.poll() is None:
			self.arret_demande = True
			self.bouton_arreter.configure(state="disabled")
			self.statut.set("Arrêt du téléchargement...")

			try:
				resultat = subprocess.run(
					[
						"taskkill",
						"/F",
						"/T",
						"/PID",
						str(processus.pid)
					],
					capture_output=True,
					text=True,
					encoding="utf-8",
					errors="replace",
					check=False
				)

			except OSError as erreur:
				self.arret_demande = False
				self.bouton_arreter.configure(state="normal")
				self.statut.set(f"Impossible d'arrêter : {erreur}")

		else:
			self.statut.set("Aucun téléchargement en cours")

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

		playlist = self.playlist.get()
		selection = None

		if playlist == "custom":
			selection = self.selection_playlist.get().strip()

			if not selection:
				self.statut.set(
					"Indique les éléments à télécharger."
				)
				self.champ_selection.focus_set()
				return

		commande = creer_commande(
			url,
			format_choisi,
			qualite,
			playlist,
			selection,
			dossier
		)	

		self.arret_demande = False
		self.bouton_telecharger.configure(state="disabled")
		self.bouton_arreter.configure(state="normal")
		self.statut.set("Téléchargement en cours...")

		thread = threading.Thread(
			target=self.executer_telechargement,
			args=(commande,),
			daemon=True
		)
		thread.start()

	def executer_telechargement(self, commande):
		import re

		try:
			self.processus = subprocess.Popen(
				commande,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				encoding="utf-8",
				errors="replace",
				bufsize=1
			)

			for ligne in self.processus.stdout:
				correspondance = re.search(
					r"\[download\]\s+(\d+(?:\.\d+)?)%",
					ligne
				)

				if correspondance:
					pourcentage = float(
						correspondance.group(1)
					)

					self.root.after(
						0,
						self.actualiser_progression,
						pourcentage,
						ligne.strip()
					)

			code_retour = self.processus.wait()

			if self.arret_demande:
				message = "Téléchargement arrêté."
			elif code_retour == 0:
				message = "Téléchargement terminé."
			else:
				message = (
					f"Echec du téléchargement "
					f"(code {code_retour})"
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

	def actualiser_progression(self, pourcentage, details):
		import re

		self.progression.set(pourcentage)
		self.details_progression.set(
			f"Progression : {pourcentage:.0f} %"
		)

		taille = re.search(
			r"of\s+~?\s*([\d.]+\s*[KMGTP]?i?B)",
			details
		)

		vitesse = re.search(
			r"at\s+([\d.]+\s*[KMGTP]?i?B/s)",
			details
		)

		temps = re.search(
			r"ETA\s+(\d+:\d+(?::\d+)?)",
			details
		)

		self.taille_telechargee.set(
			f"Téléchargé : {taille.group(1)}"
			if taille else "Téléchargé : -"
		)

		if vitesse:
			self.vitesse.set(
				f"Vitesse : {vitesse.group(1)}"
			)
		else:
			self.vitesse.set("Vitesse : -")

		if temps:			
			self.temps_restant.set(
				f"Temps restant : {temps.group(1)}"
			)
		else:
			self.temps_restant.set("Temps restant : -")


	def terminer_telechargement(self, message):
		self.progression.set(100 if message == "Téléchargement terminé." else 0)
		self.statut.set(message)
		self.bouton_telecharger.configure(state="normal")
		self.bouton_arreter.configure(state="disabled")
		self.processus = None

def lancer_interface():
	root = tk.Tk()
	YtDlpToolApp(root)
	root.mainloop()


if __name__== "__main__":
	lancer_interface()