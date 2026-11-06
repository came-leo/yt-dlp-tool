import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import DownloadCancelled

from downloader import creer_options_api, selection_playlist_valide
import historique
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
		self.root.geometry("800x640")
		self.root.minsize(740, 580)
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
		espacement_section = 16
		self.root.configure(fg_color=carte)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_rowconfigure(1, weight=1)
		self.couleur_accent_onglet = accent
		self.couleur_survol_onglet = survol_accent
		self.couleur_texte_onglet = texte
		self.boutons_onglets = {}
		barre_onglets = ctk.CTkFrame(self.root, fg_color="transparent")
		barre_onglets.grid(row=0, column=0, sticky="ew", padx=32, pady=(18, 8))
		for colonne, nom in enumerate(("Accueil", "Historique", "Paramètres")):
			bouton = ctk.CTkButton(
				barre_onglets,
				text=nom,
				width=110,
				height=36,
				corner_radius=8,
				command=lambda onglet=nom: self.selectionner_onglet(onglet)
			)
			bouton.grid(row=0, column=colonne, padx=(0, 12))
			self.boutons_onglets[nom] = bouton

		self.conteneur_onglets = ctk.CTkFrame(
			self.root,
			fg_color="transparent"
		)
		self.conteneur_onglets.grid(row=1, column=0, sticky="nsew")
		self.conteneur_onglets.grid_columnconfigure(0, weight=1)
		self.conteneur_onglets.grid_rowconfigure(0, weight=1)
		self.pages = {}
		for nom in ("Accueil", "Historique", "Paramètres"):
			page = ctk.CTkFrame(self.conteneur_onglets, fg_color="transparent")
			page.grid(row=0, column=0, sticky="nsew")
			page.grid_remove()
			self.pages[nom] = page
		self.selectionner_onglet("Accueil")

		principal = self.pages["Accueil"]
		principal.grid_columnconfigure(0, weight=1)
		principal.grid_rowconfigure(2, weight=1)

		entete = ctk.CTkFrame(principal, fg_color="transparent")
		entete.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 14))
		entete.grid_columnconfigure(0, weight=1)
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
		self.ligne_options = ligne_options
		ligne_options.grid_columnconfigure(0, weight=0)
		ligne_options.grid_columnconfigure(1, weight=0)
		ligne_options.grid_columnconfigure(2, weight=0)
		ctk.CTkLabel(
			ligne_options,
			text="Qualité",
			text_color=texte,
			font=("Segoe UI", 12, "bold")
		).grid(row=0, column=0, sticky="w", pady=(0, 6))
		ctk.CTkLabel(
			ligne_options,
			text="Playlist",
			text_color=texte,
			font=("Segoe UI", 12, "bold")
		).grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 6))

		self.list_qualite = ctk.CTkComboBox(
			ligne_options,
			values=["480p", "720p", "1080p", "2K", "4K"],
			variable=self.qualite,
			width=130,
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
			row=1,
			column=0,
			sticky="ew",
			padx=(0, 6)
		)
		self.list_playlist = ctk.CTkComboBox(
			ligne_options,
			values=[
				"Un élément",
				"Toute la playlist",
				"Sélection personnalisée",
			],
			variable=self.option_playlist,
			width=155,
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
			row=1,
			column=1,
			sticky="ew",
			padx=(6, 0)
		)

		self.zone_selection = ctk.CTkFrame(
			ligne_options,
			fg_color="transparent",
			width=180
		)
		self.zone_selection.grid(
			row=0,
			column=2,
			rowspan=2,
			sticky="nsew",
			padx=(12, 0)
		)
		self.zone_selection.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			self.zone_selection,
			text="Sélection",
			text_color=texte,
			font=("Segoe UI", 12, "bold")
		).grid(row=0, column=0, sticky="w", pady=(0, 6))
		self.champ_selection = ctk.CTkEntry(
			self.zone_selection,
			textvariable=self.selection_playlist,
			height=38,
			corner_radius=8,
			border_color=bordure,
			fg_color=fond_saisie,
			placeholder_text="Ex. : 1, 3, 5-10"
		)
		self.champ_selection.grid(
			row=1,
			column=0,
			sticky="ew"
		)
		self.zone_selection.grid_remove()

		actions = ctk.CTkFrame(contenu, fg_color="transparent")
		actions.grid(
			row=4,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		actions.grid_columnconfigure(0, weight=0)
		actions.grid_columnconfigure(1, weight=0)
		self.bouton_telecharger = ctk.CTkButton(
			actions,
			text="Télécharger",
			width=260,
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
			padx=(8, 0)
		)
		self.bouton_annuler = ctk.CTkButton(
			actions,
			text="Annuler",
			width=130,
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
			padx=(0, 8)
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
		self.creer_vue_parametres()

	def selectionner_onglet(self, nom):
		for titre, page in self.pages.items():
			if titre == nom:
				page.grid()
				self.boutons_onglets[titre].configure(
					fg_color=self.couleur_accent_onglet,
					hover_color=self.couleur_survol_onglet,
					text_color="#ffffff"
				)
			else:
				page.grid_remove()
				self.boutons_onglets[titre].configure(
					fg_color="transparent",
					hover_color=("#eeeeee", "#3a3a3a"),
					text_color=self.couleur_texte_onglet
				)

	# Paramètres de l'application
	def creer_vue_parametres(self):
		self.vue_parametres = self.pages["Paramètres"]
		self.vue_parametres.grid_columnconfigure(0, weight=1)
		self.vue_parametres.grid_rowconfigure(0, weight=1)

		couleur_texte = ("#252525", "#f4f4f4")
		couleur_secondaire = ("#666666", "#b8b8b8")
		couleur_bordure = ("#d0d0d0", "#4a4a4a")
		fond_bouton = ("#eeeeee", "#383838")
		survol_bouton = ("#dddddd", "#454545")
		couleur_accent = ("#C44732", "#C0503D")
		couleur_survol = ("#B33B2B", "#A63F30")

		contenu = ctk.CTkFrame(
			self.vue_parametres,
			fg_color="transparent"
		)
		contenu.grid(row=0, column=0, sticky="nsew", padx=32, pady=28)
		contenu.grid_columnconfigure(0, weight=1)

		entete = ctk.CTkFrame(contenu, fg_color="transparent")
		entete.grid(row=0, column=0, sticky="ew", pady=(0, 18))
		ctk.CTkLabel(
			entete,
			text="Paramètres",
			text_color=couleur_texte,
			font=("Segoe UI", 20, "bold")
		).grid(row=0, column=0, sticky="w")

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
			width=180,
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
		self.creer_vue_historique()

	def creer_vue_historique(self):
		self.vue_historique = self.pages["Historique"]
		self.vue_historique.grid_columnconfigure(0, weight=1)
		self.vue_historique.grid_rowconfigure(0, weight=1)
		contenu = ctk.CTkFrame(self.vue_historique, fg_color="transparent")
		contenu.grid(row=0, column=0, sticky="nsew", padx=32, pady=28)
		contenu.grid_columnconfigure(0, weight=1)
		contenu.grid_rowconfigure(1, weight=1)
		entete = ctk.CTkFrame(contenu, fg_color="transparent")
		entete.grid(row=0, column=0, sticky="ew", pady=(0, 16))
		entete.grid_columnconfigure(1, weight=1)
		ctk.CTkLabel(
			entete,
			text="Historique",
			font=("Segoe UI", 20, "bold")
		).grid(row=0, column=0, sticky="w")
		self.bouton_effacer_historique = ctk.CTkButton(
			entete,
			text="Effacer tout",
			width=100,
			height=34,
			command=self.effacer_historique
		)
		self.bouton_effacer_historique.grid(row=0, column=2, sticky="e")
		self.liste_historique = ctk.CTkScrollableFrame(
			contenu,
			fg_color="transparent"
		)
		self.liste_historique.grid(row=1, column=0, sticky="nsew")
		self.etat_historique = ctk.CTkLabel(
			contenu,
			text="",
			anchor="w"
		)
		self.etat_historique.grid(row=2, column=0, sticky="ew", pady=(8, 0))
		self.actualiser_historique()

	def actualiser_historique(self):
		for widget in self.liste_historique.winfo_children():
			widget.destroy()
		try:
			telechargements = historique.lister()
		except Exception as erreur:
			self.etat_historique.configure(text=f"Impossible de lire l’historique : {erreur}")
			return
		self.bouton_effacer_historique.configure(
			state="normal" if telechargements else "disabled"
		)
		if not telechargements:
			self.etat_historique.configure(text="Aucun téléchargement enregistré.")
			return
		self.etat_historique.configure(text="")
		for identifiant, chemin, type_fichier, taille, date in telechargements:
			ligne = ctk.CTkFrame(self.liste_historique)
			ligne.pack(fill="x", pady=5)
			ligne.grid_columnconfigure(0, weight=1)
			ctk.CTkLabel(
				ligne,
				text=os.path.basename(chemin),
				anchor="w",
				font=("Segoe UI", 13, "bold")
			).grid(row=0, column=0, columnspan=3, sticky="ew", padx=12, pady=(9, 2))
			ctk.CTkLabel(
				ligne,
				text=f"{type_fichier} · {self.formater_taille(taille)} · {date}",
				anchor="w"
			).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 9))
			ctk.CTkButton(
				ligne,
				text="Dossier",
				width=78,
				command=lambda p=chemin: self.ouvrir_dossier_fichier(p)
			).grid(row=1, column=1, padx=4, pady=(0, 9))
			ctk.CTkButton(
				ligne,
				text="Effacer",
				width=78,
				command=lambda i=identifiant: self.effacer_telechargement(i)
			).grid(row=1, column=2, padx=(4, 12), pady=(0, 9))

	@staticmethod
	def formater_taille(taille):
		for unite in ("o", "Ko", "Mo", "Go", "To"):
			if taille < 1000 or unite == "To":
				return f"{taille:.0f} {unite}"
			taille /= 1000

	def ouvrir_dossier_fichier(self, chemin):
		if not os.path.isfile(chemin):
			self.etat_historique.configure(text="Le fichier n’existe plus à cet emplacement.")
			return
		try:
			dossier = os.path.dirname(chemin)
			if os.name == "nt":
				os.startfile(dossier)
			elif sys.platform == "darwin":
				subprocess.Popen(["open", dossier])
			else:
				subprocess.Popen(["xdg-open", dossier])
		except OSError as erreur:
			self.etat_historique.configure(text=f"Impossible d’ouvrir le dossier : {erreur}")

	def effacer_telechargement(self, identifiant):
		try:
			historique.supprimer(identifiant)
			self.actualiser_historique()
		except Exception as erreur:
			self.etat_historique.configure(text=f"Impossible de modifier l’historique : {erreur}")

	def effacer_historique(self):
		if not messagebox.askyesno(
			"Effacer l’historique",
			"Effacer toutes les entrées de l’historique ? Les fichiers téléchargés seront conservés.",
			parent=self.root
		):
			return
		try:
			historique.supprimer_tout()
			self.actualiser_historique()
		except Exception as erreur:
			self.etat_historique.configure(text=f"Impossible de modifier l’historique : {erreur}")

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
			self.ligne_options.grid_columnconfigure(2, weight=0)
			self.zone_selection.grid()
		else:
			self.ligne_options.grid_columnconfigure(2, weight=0)
			self.zone_selection.grid_remove()
			self.selection_playlist.set("")

	# Lancement, suivi et annulation du téléchargement
	def annuler_telechargement(self):
		if self.bouton_telecharger.cget("state") == "disabled":
			self.arret_demande = True
			self.statut.set("Annulation du téléchargement...")
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

		self.arret_demande = False
		self.erreur_telechargement = ""
		self.erreur_historique = ""
		self.bouton_telecharger.configure(state="disabled")
		self.statut.set("Téléchargement en cours...")
		progress_hook = lambda progression: self.verifier_annulation(
			progression,
			positions_playlist,
			playlist == "unique"
		)

		thread = threading.Thread(
			target=self.executer_telechargement,
			args=(
				url,
				creer_options_api(
					format_choisi,
					qualite,
					playlist,
					selection,
					dossier,
					progress_hook,
					self.enregistrer_fichier_termine,
				),
			),
			daemon=True
		)
		thread.start()

	def executer_telechargement(
		self,
		url,
		options
	):
		options["logger"] = self
		try:
			with yt_dlp.YoutubeDL(options) as telechargeur:
				code_retour = telechargeur.download([url])

			if self.arret_demande:
				message = "Téléchargement arrêté."
			elif code_retour == 0:
				message = "Téléchargement terminé."
			else:
				message = "Échec du téléchargement."
				if self.erreur_telechargement:
					message += f" {self.erreur_telechargement[:180]}"
		except DownloadCancelled:
			message = "Téléchargement arrêté."
		except Exception as erreur:
			message = f"Erreur de téléchargement : {erreur}"

		if self.erreur_historique and message == "Téléchargement terminé.":
			message = f"Téléchargement terminé (historique non enregistré : {self.erreur_historique[:120]})"

		self.root.after(
			0,
			self.terminer_telechargement,
			message
		)

	def verifier_annulation(self, progression, positions_playlist, element_unique):
		if self.arret_demande:
			raise DownloadCancelled("Téléchargement annulé depuis l’interface")
		if progression.get("status") != "downloading":
			return
		info = progression.get("info_dict", {})
		index = info.get("playlist_index")
		total = info.get("playlist_count")
		position = str(index) if index else ""
		if element_unique:
			position, total = "1", "1"
		elif positions_playlist and index:
			try:
				position = str(positions_playlist.index(int(index)) + 1)
				total = str(len(positions_playlist))
			except ValueError:
				pass
		self.root.after(
			0,
			self.actualiser_progression_api,
			progression,
			position,
			str(total or "")
		)

	def actualiser_progression_api(self, progression, position="", total=""):
		if progression.get("status") not in ("downloading", "finished"):
			return
		taille_totale = progression.get("total_bytes") or progression.get("total_bytes_estimate")
		taille = progression.get("downloaded_bytes", 0)
		pourcentage = 100 if progression.get("status") == "finished" else (
			100 * taille / taille_totale if taille_totale else 0
		)
		self.barre_progression.set(min(pourcentage, 100) / 100)
		self.pourcentage_progression.set(f"{pourcentage:.0f} %")
		indicateurs = []
		if taille_totale:
			indicateurs.append(
				f"Taille : {self.formater_taille(taille)} / {self.formater_taille(taille_totale)}"
			)
		if progression.get("speed"):
			indicateurs.append(f"Vitesse : {self.formater_taille(progression['speed'])}/s")
		if progression.get("eta") is not None:
			indicateurs.append(f"Temps restant : {self.formater_temps(progression['eta'])}")
		compteur = f"{position}/{total}    " if position and total else ""
		self.details_progression.set(compteur + "    ".join(indicateurs))

	@staticmethod
	def formater_temps(secondes):
		secondes = max(0, int(secondes))
		heures, reste = divmod(secondes, 3600)
		minutes, secondes = divmod(reste, 60)
		return f"{heures}:{minutes:02}:{secondes:02}" if heures else f"{minutes}:{secondes:02}"

	def enregistrer_fichier_termine(self, chemin):
		try:
			historique.ajouter(chemin)
		except Exception as erreur:
			self.erreur_historique = str(erreur)
		else:
			self.root.after(0, self.actualiser_historique_si_visible)

	def actualiser_historique_si_visible(self):
		self.actualiser_historique()

	def debug(self, message):
		pass

	def warning(self, message):
		pass

	def error(self, message, *args, **kwargs):
		self.erreur_telechargement = message

	# Affichage de l'avancement et du résultat
	def terminer_telechargement(self, message):
		reussi = message.startswith("Téléchargement terminé")
		self.barre_progression.set(
			1 if reussi else 0
		)
		self.statut.set(message)

		if message.startswith("Téléchargement terminé") or message == "Téléchargement arrêté.":
			self.reinitialiser_choix()
			self.pourcentage_progression.set("")
			self.details_progression.set("En attente d'un téléchargement")

		self.bouton_telecharger.configure(state="normal")


def lancer_interface():
	root = ctk.CTk()
	YtDlpToolApp(root)
	root.mainloop()


if __name__ == "__main__":
	lancer_interface()
