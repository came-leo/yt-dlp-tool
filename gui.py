import re
import os
import signal
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from downloader import creer_commande, selection_playlist_valide
from main import charger_dossier, enregistrer_dossier


class YtDlpToolApp:
	def __init__(self, root):
		self.root = root
		self.root.title("yt-dlp-tool")
		self.root.geometry("880x720")
		self.root.minsize(720, 620)
		self.root.configure(fg_color="#2d2d2d")

		ctk.set_appearance_mode("dark")
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
		self.processus = None
		self.arret_demande = False

		self.creer_interface()
		self.root.after(100, self.champ_url.focus_set)

	# Construction de l'interface
	def creer_interface(self):
		carte = "#2d2d2d"
		bordure = "#4a4a4a"
		texte = "#f4f4f4"
		secondaire = "#b8b8b8"
		accent = "#C0503D"
		espacement_section = 18

		# La fenêtre sert directement de conteneur principal.
		principal = self.root
		principal.grid_columnconfigure(0, weight=1)

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

		separateur = ctk.CTkFrame(principal, height=1, fg_color="#414141")
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
			fg_color=carte,
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
			hover_color="#A63F30",
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
			hover_color="#A63F30",
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
			fg_color=carte,
			button_color="#414141",
			button_hover_color="#4b4b4b",
			dropdown_fg_color="#343434",
			dropdown_hover_color="#414141",
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
			fg_color=carte,
			button_color="#414141",
			button_hover_color="#4b4b4b",
			dropdown_fg_color="#343434",
			dropdown_hover_color="#414141",
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
			fg_color=carte,
			placeholder_text="Numéros, par exemple : 1, 2, 3-5"
		)
		self.champ_selection.grid(
			row=0,
			column=2,
			sticky="ew"
		)
		self.champ_selection.grid_remove()

		etiquette(contenu, "Dossier de destination", 4)
		ligne_dossier = ctk.CTkFrame(contenu, fg_color="transparent")
		ligne_dossier.grid(
			row=5,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		ligne_dossier.grid_columnconfigure(0, weight=1)
		self.champ_dossier = ctk.CTkEntry(
			ligne_dossier,
			textvariable=self.dossier,
			height=46,
			corner_radius=9,
			border_color=bordure,
			fg_color=carte,
			state="readonly"
		)
		self.champ_dossier.grid(row=0, column=0, sticky="ew", padx=(0, 8))
		ctk.CTkButton(
			ligne_dossier,
			text="Choisir un dossier…",
			width=150,
			height=46,
			corner_radius=9,
			fg_color="#383838",
			hover_color="#454545",
			border_width=1,
			border_color=bordure,
			command=self.choisir_dossier
		).grid(row=0, column=1)

		actions = ctk.CTkFrame(contenu, fg_color="transparent")
		actions.grid(
			row=6,
			column=0,
			sticky="ew",
			pady=(0, espacement_section)
		)
		actions.grid_columnconfigure(0, weight=1)
		self.bouton_telecharger = ctk.CTkButton(
			actions,
			text="Télécharger",
			height=52,
			corner_radius=10,
			fg_color=accent,
			hover_color="#A63F30",
			font=("Segoe UI", 15, "bold"),
			command=self.telecharger
		)
		self.bouton_telecharger.grid(row=0, column=0, sticky="ew")
		self.bouton_arreter = ctk.CTkButton(
			actions,
			text="Arrêter le téléchargement",
			height=38,
			corner_radius=9,
			fg_color="#383838",
			hover_color="#454545",
			border_width=1,
			border_color=bordure,
			command=self.arreter_telechargement
		)
		self.bouton_arreter.grid(
			row=1,
			column=0,
			sticky="ew",
			pady=(8, 0)
		)
		self.bouton_arreter.grid_remove()

		progression_entete = ctk.CTkFrame(contenu, fg_color="transparent")
		progression_entete.grid(row=7, column=0, sticky="ew", pady=(0, 6))
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
			progress_color=accent,
			fg_color="#1d1d1d"
		)
		self.barre_progression.grid(row=8, column=0, sticky="ew")
		self.barre_progression.set(0)
		self.infos_progression = ctk.CTkLabel(
			contenu,
			textvariable=self.details_progression,
			text_color=secondaire,
			font=("Segoe UI", 11)
		)
		self.infos_progression.grid(row=9, column=0, sticky="w", pady=(6, 0))

		self.actualiser_qualite()
		self.changer_playlist("Un élément")

	# Gestion des préférences de téléchargement
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

	# Lancement, suivi et arrêt du téléchargement
	def arreter_telechargement(self):
		processus = self.processus

		if processus is None:
			if self.bouton_telecharger.cget("state") == "disabled":
				self.arret_demande = True
				self.bouton_arreter.configure(state="disabled")
				self.statut.set("Arrêt du téléchargement...")
			else:
				self.statut.set("Aucun téléchargement en cours")
			return

		if processus.poll() is None:
			self.arret_demande = True
			self.bouton_arreter.configure(state="disabled")
			self.bouton_arreter.grid()
			self.statut.set("Arrêt du téléchargement...")

			try:
				self.arreter_processus(processus)

			except OSError as erreur:
				self.arret_demande = False
				self.bouton_arreter.configure(state="normal")
				self.statut.set(f"Impossible d'arrêter : {erreur}")

		else:
			self.statut.set("Aucun téléchargement en cours")

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

		if playlist == "custom":
			selection = self.selection_playlist.get().strip()

			if not selection_playlist_valide(selection):
				self.statut.set(
					"Sélectionne les éléments sous la forme 1, 2, 3-5."
				)
				self.champ_selection.focus_set()
				return

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
				"%(progress._eta_str)s"
			),
		]

		self.arret_demande = False
		self.bouton_telecharger.configure(state="disabled")
		self.bouton_arreter.configure(state="normal")
		self.bouton_arreter.grid()
		self.statut.set("Téléchargement en cours...")

		thread = threading.Thread(
			target=self.executer_telechargement,
			args=(commande,),
			daemon=True
		)
		thread.start()

	def executer_telechargement(self, commande):
		try:
			detail_erreur = None
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
				if "[error]" in ligne.lower() or "error:" in ligne.lower():
					detail_erreur = ligne.strip()

				valeurs = ligne.strip().split("|", 3)
				if len(valeurs) == 4:
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

					self.root.after(
						0,
						self.actualiser_progression,
						pourcentage,
						details
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
	def actualiser_progression(self, pourcentage, details):
		self.barre_progression.set(pourcentage / 100)
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

		indicateurs = []
		if taille:
			indicateurs.append(f"Taille : {taille.group(1)}")
		if vitesse:
			indicateurs.append(f"Vitesse : {vitesse.group(1)}")
		if temps:
			indicateurs.append(f"Temps restant : {temps.group(1)}")
		if indicateurs:
			self.details_progression.set(
				f"{pourcentage:.0f} %    "
				+ "    ".join(indicateurs)
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
			self.url.set("")
			self.format_choisi.set("video")
			self.qualite.set("720p")
			self.actualiser_qualite()
			self.option_playlist.set("Un élément")
			self.changer_playlist("Un élément")

		self.bouton_telecharger.configure(state="normal")
		self.bouton_arreter.configure(state="disabled")
		self.bouton_arreter.grid_remove()
		self.processus = None


def lancer_interface():
	root = ctk.CTk()
	YtDlpToolApp(root)
	root.mainloop()


if __name__ == "__main__":
	lancer_interface()
