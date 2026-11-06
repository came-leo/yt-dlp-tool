import re
import os
import signal
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from downloader import creer_commande, selection_playlist_valide
from main import (
	charger_dossier,
	charger_theme,
	enregistrer_dossier,
	enregistrer_theme,
	mettre_a_jour
)


class YtDlpToolApp:
	def __init__(self, root):
		self.root = root
		self.root.title("yt-dlp-tool")
		self.root.geometry("720x520")
		self.root.minsize(680, 490)
		self.mode_clair = charger_theme() == "light"
		ctk.set_appearance_mode(
			"light" if self.mode_clair else "dark"
		)
		ctk.set_default_color_theme("dark-blue")

		self.dossier = tk.StringVar(value=charger_dossier())
		self.url = tk.StringVar()
		self.format_choisi = tk.StringVar(value="video")
		self.qualite = tk.StringVar(value="720p")
		self.playlist = tk.StringVar(value="unique")
		self.option_playlist = tk.StringVar(value="Un élément")
		self.selection_playlist = tk.StringVar()
		self.statut = tk.StringVar(value="Prêt")
		self.details_progression = tk.StringVar(
			value="En attente d'un téléchargement"
		)
		self.pourcentage_progression = tk.StringVar()
		self.processus = None
		self.arret_demande = False
		self.mise_a_jour_en_cours = False

		self.creer_interface()
		self.root.after(100, self.champ_url.focus_set)

	# Construction de l'interface
	def creer_interface(self):
		carte = ("#ffffff", "#2d2d2d")
		fond_saisie = ("#ffffff", "#2d2d2d")
		fond_bouton = ("#eeeeee", "#383838")
		survol_bouton = ("#dddddd", "#454545")
		bordure = ("#d0d0d0", "#4a4a4a")
		texte = ("#252525", "#f4f4f4")
		secondaire = ("#666666", "#b8b8b8")
		accent = ("#C44732", "#C0503D")
		survol_accent = ("#B33B2B", "#A63F30")
		espacement_section = 18
		self.root.configure(fg_color=carte)

		# La fenêtre sert directement de conteneur principal.
		principal = self.root
		principal.grid_columnconfigure(0, weight=1)
		principal.grid_rowconfigure(2, weight=1)

		entete = ctk.CTkFrame(principal, fg_color="transparent")
		entete.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 14))
		entete.grid_columnconfigure(0, weight=1)
		self.bouton_parametres = ctk.CTkButton(
			entete,
			text="⚙",
			width=36,
			height=36,
			corner_radius=18,
			fg_color="transparent",
			hover_color=("#e8e8e8", "#414141"),
			text_color=texte,
			font=("Segoe UI Symbol", 19),
			command=self.ouvrir_parametres
		)
		self.bouton_parametres.grid(
			row=0,
			column=1,
			rowspan=2,
			sticky="ne",
			padx=(12, 0)
		)
		ctk.CTkLabel(
			entete,
			text="yt-dlp-tool",
			text_color=texte,
			font=("Segoe UI", 21, "bold")
		).grid(row=0, column=0, sticky="sw")
		ctk.CTkLabel(
			entete,
			text="Téléchargeur multimédia",
			text_color=secondaire,
			font=("Segoe UI", 12)
		).grid(row=1, column=0, sticky="nw")

		separateur = ctk.CTkFrame(
			principal,
			height=1,
			fg_color=("#d8d8d8", "#414141")
		)
		separateur.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 20))

		contenu = ctk.CTkFrame(principal, fg_color="transparent")
		contenu.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0, 28))
		contenu.grid_columnconfigure(0, weight=1)

		def etiquette(parent, titre, row, pady=(0, 6), column=0):
			ctk.CTkLabel(
				parent,
				text=titre,
				text_color=texte,
				font=("Segoe UI", 13, "bold")
			).grid(
				row=row,
				column=column,
				sticky="w",
				pady=pady
			)

		etiquette(contenu, "URL de la vidéo ou de la playlist", 0)
		self.champ_url = ctk.CTkEntry(
			contenu,
			textvariable=self.url,
			height=46,
			corner_radius=9,
			border_color=bordure,
			fg_color=fond_saisie,
			placeholder_text="https://www.youtube.com/..."
		)
		self.champ_url.grid(
			row=1,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		self.menu_url = tk.Menu(self.root, tearoff=False)
		self.menu_url.add_command(
			label="Couper",
			command=lambda: self.champ_url._entry.event_generate("<<Cut>>")
		)
		self.menu_url.add_command(
			label="Copier",
			command=lambda: self.champ_url._entry.event_generate("<<Copy>>")
		)
		self.menu_url.add_command(
			label="Coller",
			command=lambda: self.champ_url._entry.event_generate("<<Paste>>")
		)
		self.menu_url.add_separator()
		self.menu_url.add_command(
			label="Tout sélectionner",
			command=self.selectionner_toute_url
		)
		self.champ_url._entry.bind(
			"<Button-3>",
			self.afficher_menu_url
		)

		formats = ctk.CTkFrame(contenu, fg_color="transparent")
		formats.grid(
			row=2,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		self.radio_video = ctk.CTkRadioButton(
			formats,
			text="Vidéo MP4",
			variable=self.format_choisi,
			value="video",
			width=145,
			height=28,
			radiobutton_width=18,
			radiobutton_height=18,
			corner_radius=10,
			border_width_unchecked=2,
			border_width_checked=5,
			fg_color=accent,
			hover_color=survol_accent,
			border_color=bordure,
			text_color=texte,
			font=("Segoe UI", 13),
			command=self.actualiser_qualite
		)
		self.radio_video.pack(side="left", padx=(0, 24))
		self.radio_audio = ctk.CTkRadioButton(
			formats,
			text="Audio MP3",
			variable=self.format_choisi,
			value="mp3",
			width=145,
			height=28,
			radiobutton_width=18,
			radiobutton_height=18,
			corner_radius=10,
			border_width_unchecked=2,
			border_width_checked=5,
			fg_color=accent,
			hover_color=survol_accent,
			border_color=bordure,
			text_color=texte,
			font=("Segoe UI", 13),
			command=self.actualiser_qualite
		)
		self.radio_audio.pack(side="left")

		ligne_options = ctk.CTkFrame(contenu, fg_color="transparent")
		ligne_options.grid(
			row=3,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		ligne_options.grid_columnconfigure(2, weight=1)

		self.list_qualite = ctk.CTkComboBox(
			ligne_options,
			values=["480p", "720p", "1080p", "2K", "4K"],
			variable=self.qualite,
			width=160,
			height=38,
			corner_radius=8,
			border_color=bordure,
			fg_color=fond_saisie,
			button_color=("#e5e5e5", "#414141"),
			button_hover_color=("#d6d6d6", "#4b4b4b"),
			dropdown_fg_color=("#ffffff", "#343434"),
			dropdown_hover_color=("#e8e8e8", "#414141"),
			dropdown_text_color=texte,
			text_color=texte,
		)
		self.list_qualite.grid(
			row=0,
			column=0,
			sticky="w",
			padx=(0, 12)
		)
		self.list_playlist = ctk.CTkComboBox(
			ligne_options,
			values=[
				"Un élément",
				"Toute la playlist",
				"Sélection personnalisée",
			],
			variable=self.option_playlist,
			width=210,
			height=38,
			corner_radius=8,
			border_color=bordure,
			fg_color=fond_saisie,
			button_color=("#e5e5e5", "#414141"),
			button_hover_color=("#d6d6d6", "#4b4b4b"),
			dropdown_fg_color=("#ffffff", "#343434"),
			dropdown_hover_color=("#e8e8e8", "#414141"),
			dropdown_text_color=texte,
			text_color=texte,
			command=self.changer_playlist,
		)
		self.list_playlist.grid(
			row=0,
			column=1,
			sticky="w",
			padx=(0, 12)
		)

		self.champ_selection = ctk.CTkEntry(
			ligne_options,
			textvariable=self.selection_playlist,
			height=38,
			corner_radius=8,
			border_color=bordure,
			fg_color=fond_saisie,
			placeholder_text="Numéros, par exemple : 1, 2, 3-5"
		)
		self.champ_selection.grid(
			row=0,
			column=2,
			sticky="ew"
		)
		self.champ_selection.grid_remove()

		actions = ctk.CTkFrame(contenu, fg_color="transparent")
		actions.grid(
			row=4,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		actions.grid_columnconfigure(0, weight=1)
		actions.grid_columnconfigure(1, weight=2)
		self.bouton_telecharger = ctk.CTkButton(
			actions,
			text="Télécharger",
			height=52,
			corner_radius=10,
			fg_color=accent,
			hover_color=survol_accent,
			text_color="#FFFFFF",
			font=("Segoe UI", 15, "bold"),
			command=self.telecharger
		)
		self.bouton_telecharger.grid(
			row=0,
			column=1,
			sticky="ew",
			padx=(5, 0)
		)
		self.bouton_annuler = ctk.CTkButton(
			actions,
			text="Annuler",
			height=52,
			corner_radius=9,
			fg_color=("#555555", "#444444"),
			hover_color=("#444444", "#555555"),
			border_width=1,
			border_color=bordure,
			text_color="#FFFFFF",
			font=("Segoe UI", 15, "bold"),
			command=self.annuler_telechargement
		)
		self.bouton_annuler.grid(
			row=0,
			column=0,
			sticky="ew",
			padx=(0, 5)
		)

		progression_entete = ctk.CTkFrame(contenu, fg_color="transparent")
		progression_entete.grid(row=5, column=0, sticky="ew", pady=(0, 6))
		progression_entete.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			progression_entete,
			text="Progression",
			text_color=texte,
			font=("Segoe UI", 13, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			progression_entete,
			textvariable=self.statut,
			text_color=secondaire
		).grid(row=0, column=1, sticky="e")
		self.barre_progression = ctk.CTkProgressBar(
			contenu,
			height=8,
			corner_radius=4,
			progress_color="#4f9e63",
			fg_color=("#dedede", "#1d1d1d")
		)
		self.barre_progression.grid(row=6, column=0, sticky="ew")
		self.barre_progression.set(0)
		ligne_infos_progression = ctk.CTkFrame(
			contenu,
			fg_color="transparent"
		)
		ligne_infos_progression.grid(
			row=7,
			column=0,
			sticky="ew",
			pady=(6, 0)
		)
		ligne_infos_progression.grid_columnconfigure(0, weight=1)
		self.infos_progression = ctk.CTkLabel(
			ligne_infos_progression,
			textvariable=self.details_progression,
			text_color=secondaire,
			font=("Segoe UI", 11)
		)
		self.infos_progression.grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			ligne_infos_progression,
			textvariable=self.pourcentage_progression,
			text_color=secondaire,
			font=("Segoe UI", 11)
		).grid(row=0, column=1, sticky="e")

		self.actualiser_qualite()
		self.changer_playlist("Un élément")
		self.entete = entete
		self.separateur = separateur
		self.contenu = contenu
		self.creer_vue_parametres()

	# Paramètres de l'application
	def ouvrir_parametres(self):
		self.entete.grid_remove()
		self.separateur.grid_remove()
		self.contenu.grid_remove()
		self.vue_parametres.grid(
			row=0,
			column=0,
			rowspan=3,
			sticky="nsew",
			padx=32,
			pady=28
		)

	def retour_menu_principal(self):
		self.vue_parametres.grid_remove()
		self.entete.grid()
		self.separateur.grid()
		self.contenu.grid()
		self.champ_url.focus_set()

	def creer_vue_parametres(self):
		self.vue_parametres = ctk.CTkFrame(
			self.root,
			fg_color="transparent"
		)
		self.vue_parametres.grid_columnconfigure(0, weight=1)

		couleur_texte = ("#252525", "#f4f4f4")
		couleur_secondaire = ("#666666", "#b8b8b8")
		couleur_bordure = ("#d0d0d0", "#4a4a4a")
		fond_bouton = ("#eeeeee", "#383838")
		survol_bouton = ("#dddddd", "#454545")
		couleur_accent = ("#C44732", "#C0503D")
		couleur_survol = ("#B33B2B", "#A63F30")

		contenu = self.vue_parametres

		entete = ctk.CTkFrame(contenu, fg_color="transparent")
		entete.grid(row=0, column=0, sticky="ew", pady=(0, 18))
		entete.grid_columnconfigure(1, weight=1)
		ctk.CTkButton(
			entete,
			text="← Retour",
			width=110,
			height=36,
			fg_color=fond_bouton,
			hover_color=survol_bouton,
			border_width=1,
			border_color=couleur_bordure,
			text_color=couleur_texte,
			command=self.retour_menu_principal
		).grid(row=0, column=0, sticky="w", padx=(0, 18))
		ctk.CTkLabel(
			entete,
			text="Paramètres",
			text_color=couleur_texte,
			font=("Segoe UI", 20, "bold")
		).grid(row=0, column=1, sticky="w")

		ctk.CTkLabel(
			contenu,
			text="Dossier de destination",
			text_color=couleur_texte,
			font=("Segoe UI", 13, "bold")
		).grid(row=1, column=0, sticky="w", pady=(0, 6))

		ligne_dossier = ctk.CTkFrame(contenu, fg_color="transparent")
		ligne_dossier.grid(row=2, column=0, sticky="ew", pady=(0, 18))
		ligne_dossier.grid_columnconfigure(0, weight=1)
		ctk.CTkEntry(
			ligne_dossier,
			textvariable=self.dossier,
			height=40,
			corner_radius=8,
			border_color=couleur_bordure,
			state="readonly"
		).grid(row=0, column=0, sticky="ew", padx=(0, 12))
		ctk.CTkButton(
			ligne_dossier,
			text="Choisir…",
			width=105,
			height=40,
			fg_color=fond_bouton,
			hover_color=survol_bouton,
			border_width=1,
			border_color=couleur_bordure,
			text_color=couleur_texte,
			command=self.choisir_dossier
		).grid(row=0, column=1)

		ligne_theme = ctk.CTkFrame(contenu, fg_color="transparent")
		ligne_theme.grid(row=3, column=0, sticky="w", pady=(0, 18))
		ctk.CTkLabel(
			ligne_theme,
			text="Thème",
			text_color=couleur_texte,
			font=("Segoe UI", 13, "bold")
		).grid(row=0, column=0, sticky="w", padx=(0, 12))

		self.choix_theme = ctk.CTkSegmentedButton(
			ligne_theme,
			values=["Clair", "Sombre"],
			width=200,
			height=38,
			dynamic_resizing=False,
			selected_color=couleur_accent,
			selected_hover_color=couleur_survol,
			text_color=couleur_texte,
			command=self.changer_theme
		)
		self.choix_theme.grid(row=0, column=1, sticky="w")
		self.choix_theme.set("Clair" if self.mode_clair else "Sombre")

		ligne_mise_a_jour = ctk.CTkFrame(contenu, fg_color="transparent")
		ligne_mise_a_jour.grid(row=4, column=0, sticky="w")
		self.bouton_mise_a_jour = ctk.CTkButton(
			ligne_mise_a_jour,
			text="Mise à jour de yt-dlp",
			width=0,
			height=32,
			fg_color="transparent",
			hover_color=fond_bouton,
			text_color=couleur_texte,
			font=("Segoe UI", 13, "bold"),
			command=self.lancer_mise_a_jour
		)
		self.bouton_mise_a_jour.grid(row=0, column=0, sticky="w")
		if self.mise_a_jour_en_cours:
			self.bouton_mise_a_jour.configure(state="disabled")

		self.etat_mise_a_jour = ctk.CTkLabel(
			contenu,
			text="",
			text_color=couleur_secondaire,
			wraplength=380,
			justify="left"
		)
		self.etat_mise_a_jour.grid(
			row=5,
			column=0,
			sticky="w",
			pady=(8, 0)
		)

	def changer_theme(self, theme):
		self.mode_clair = theme == "Clair"
		ctk.set_appearance_mode(
			"light" if self.mode_clair else "dark"
		)
		try:
			enregistrer_theme(
				"light" if self.mode_clair else "dark"
			)
		except OSError as erreur:
			self.statut.set(f"Thème non enregistré : {erreur}")

	def choisir_dossier(self):
		dossier = filedialog.askdirectory(
			parent=self.root,
			title="Choisir le dossier de destination",
			initialdir=self.dossier.get(),
			mustexist=True
		)

		if dossier:
			try:
				dossier = enregistrer_dossier(dossier)
				self.dossier.set(dossier)
				self.statut.set("Dossier enregistré.")
			except OSError as erreur:
				self.statut.set(f"Erreur : {erreur}")

	def lancer_mise_a_jour(self):
		if self.mise_a_jour_en_cours:
			return

		self.mise_a_jour_en_cours = True
		self.bouton_mise_a_jour.configure(state="disabled")
		self.etat_mise_a_jour.configure(text="Mise à jour en cours…")
		threading.Thread(
			target=self.executer_mise_a_jour,
			daemon=True
		).start()

	def executer_mise_a_jour(self):
		try:
			resultat = mettre_a_jour(attendre=False)
			lignes = (
				resultat.stdout + "\n" + resultat.stderr
			).strip().splitlines()
			message = lignes[-1] if lignes else "Mise à jour terminée."
			if resultat.returncode != 0:
				message = f"Échec de la mise à jour : {message}"
		except OSError as erreur:
			message = f"Mise à jour impossible : {erreur}"

		self.root.after(0, self.afficher_resultat_mise_a_jour, message)

	def afficher_resultat_mise_a_jour(self, message):
		self.mise_a_jour_en_cours = False
		self.bouton_mise_a_jour.configure(state="normal")
		self.etat_mise_a_jour.configure(text=message)

	def afficher_menu_url(self, evenement):
		try:
			self.menu_url.tk_popup(
				evenement.x_root,
				evenement.y_root
			)
		finally:
			self.menu_url.grab_release()

	def selectionner_toute_url(self):
		champ = self.champ_url._entry
		champ.focus_set()
		champ.select_range(0, tk.END)
		champ.icursor(tk.END)

	def changer_playlist(self, choix):
		valeur = {
			"Un élément": "unique",
			"Toute la playlist": "complete",
			"Sélection personnalisée": "custom",
		}[choix]
		self.playlist.set(valeur)
		self.actualiser_playlist()

	# Mise à jour des choix affichés
	def actualiser_qualite(self):
		qualite_desactivee = self.format_choisi.get() == "mp3"
		self.list_qualite.configure(
			state="disabled" if qualite_desactivee else "readonly"
		)

	def actualiser_playlist(self):
		if self.playlist.get() == "custom":
			self.champ_selection.grid()
		else:
			self.champ_selection.grid_remove()
			self.selection_playlist.set("")

	# Lancement, suivi et annulation du téléchargement
	def annuler_telechargement(self):
		processus = self.processus

		if processus is None:
			if self.bouton_telecharger.cget("state") == "disabled":
				self.arret_demande = True
				self.statut.set("Arrêt du téléchargement...")
			else:
				self.reinitialiser_choix()
				self.statut.set("Prêt")
			return

		if processus.poll() is None:
			self.arret_demande = True
			self.statut.set("Arrêt du téléchargement...")

			try:
				self.arreter_processus(processus)

			except OSError as erreur:
				self.arret_demande = False
				self.statut.set(f"Impossible d'arrêter : {erreur}")

		else:
			self.reinitialiser_choix()
			self.statut.set("Prêt")

	def reinitialiser_choix(self):
		self.url.set("")
		self.format_choisi.set("video")
		self.qualite.set("720p")
		self.actualiser_qualite()
		self.option_playlist.set("Un élément")
		self.changer_playlist("Un élément")

	def arreter_processus(self, processus):
		if os.name != "nt":
			os.killpg(processus.pid, signal.SIGTERM)
			return

		resultat = subprocess.run(
			[
				"taskkill",
				"/F",
				"/T",
				"/PID",
				str(processus.pid),
			],
			capture_output=True,
			text=True,
			encoding="utf-8",
			errors="replace",
			check=False,
		)

		if resultat.returncode != 0 and processus.poll() is None:
			detail = resultat.stderr.strip() or "taskkill a échoué."
			raise OSError(detail)

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
			qualite = {
				"480p": 480,
				"720p": 720,
				"1080p": 1080,
				"2K": 1440,
				"4K": 2160,
			}[self.qualite.get()]
			format_choisi = "qualite"

		playlist = self.playlist.get()
		selection = None
		positions_playlist = []

		if playlist == "custom":
			selection = self.selection_playlist.get().strip()

			if not selection_playlist_valide(selection):
				self.statut.set(
					"Sélectionne les éléments sous la forme 1, 2, 3-5."
				)
				self.champ_selection.focus_set()
				return

			for element in selection.split(","):
				bornes = [int(borne) for borne in element.strip().split("-")]
				debut = bornes[0]
				fin = bornes[-1]
				positions_playlist.extend(range(debut, fin + 1))

		commande = creer_commande(
			url,
			format_choisi,
			qualite,
			playlist,
			selection,
			dossier,
		)
		commande[-1:-1] = [
			"--no-colors",
			"--progress-template",
			(
				"download:%(progress._percent_str)s|"
				"%(progress._total_bytes_str)s|"
				"%(progress._speed_str)s|"
				"%(progress._eta_str)s|"
				"%(info.playlist_index)s|"
				"%(info.playlist_count)s"
			),
		]

		self.arret_demande = False
		self.bouton_telecharger.configure(state="disabled")
		self.statut.set("Téléchargement en cours...")

		thread = threading.Thread(
			target=self.executer_telechargement,
			args=(
				commande,
				positions_playlist,
				playlist == "unique"
			),
			daemon=True
		)
		thread.start()

	def executer_telechargement(
		self,
		commande,
		positions_playlist,
		element_unique
	):
		detail_erreur = None
		try:
			self.processus = subprocess.Popen(
				commande,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				encoding="utf-8",
				errors="replace",
				bufsize=1,
				start_new_session=(os.name != "nt"),
			)
			if self.arret_demande:
				self.arreter_processus(self.processus)

			for ligne in self.processus.stdout:
				ligne = ligne.strip()
				if "[error]" in ligne.lower() or "error:" in ligne.lower():
					detail_erreur = ligne

				valeurs = ligne.split("|", 5)
				if len(valeurs) == 6:
					try:
						pourcentage = float(
							valeurs[0].replace("%", "").strip()
						)
					except ValueError:
						continue

					details = (
						f"of {valeurs[1]} at {valeurs[2]} "
						f"ETA {valeurs[3]}"
					)
					position_playlist = valeurs[4].strip()
					total_playlist = valeurs[5].strip()
					if element_unique:
						position_playlist = "1"
						total_playlist = "1"
					elif (
						positions_playlist
						and position_playlist.isdigit()
					):
						try:
							position_playlist = str(
								positions_playlist.index(
									int(position_playlist)
								) + 1
							)
							total_playlist = str(
								len(positions_playlist)
							)
						except ValueError:
							pass

					self.root.after(
						0,
						self.actualiser_progression,
						pourcentage,
						details,
						position_playlist,
						total_playlist
					)

			code_retour = self.processus.wait()

			if self.arret_demande:
				message = "Téléchargement arrêté."
			elif code_retour == 0:
				message = "Téléchargement terminé."
			else:
				message = (
					f"Échec du téléchargement "
					f"(code {code_retour})"
				)
				if detail_erreur:
					message += f" : {detail_erreur[:180]}"

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

	# Affichage de l'avancement et du résultat
	def actualiser_progression(
		self,
		pourcentage,
		details,
		position_playlist="",
		total_playlist=""
	):
		self.barre_progression.set(pourcentage / 100)
		self.pourcentage_progression.set(f"{pourcentage:.0f} %")
		compteur_playlist = ""
		if (
			position_playlist.isdigit()
			and total_playlist.isdigit()
		):
			compteur_playlist = (
				f"{position_playlist}/{total_playlist}    "
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

		indicateurs = []
		if taille:
			indicateurs.append(f"Taille : {taille.group(1)}")
		if vitesse:
			indicateurs.append(f"Vitesse : {vitesse.group(1)}")
		if temps:
			indicateurs.append(f"Temps restant : {temps.group(1)}")
		self.details_progression.set(
			compteur_playlist + "    ".join(indicateurs)
		)

	def terminer_telechargement(self, message):
		reussi = message == "Téléchargement terminé."
		self.barre_progression.set(
			1 if reussi else 0
		)
		self.statut.set(message)

		if message in (
			"Téléchargement terminé.",
			"Téléchargement arrêté.",
		):
			self.reinitialiser_choix()

		self.bouton_telecharger.configure(state="normal")
		self.processus = None


def lancer_interface():
	root = ctk.CTk()
	YtDlpToolApp(root)
	root.mainloop()


if __name__ == "__main__":
	lancer_interface()
