# front/zone_visualisation.py
import customtkinter as ctk
from back.Automate import Automate
from interfaces.zone_visualisation_interface import ZoneVisualisation
from .turtle_visualizer import TurtleVisualizerImpl
from typing import List, Set

class ZoneVisualisationImpl(ZoneVisualisation):
    def __init__(self, parent):
        super().__init__(parent)
        self.text_area = ctk.CTkTextbox(self, width=400, height=200)
        self.text_area.pack(padx=10, pady=10)
        self.visualizer = TurtleVisualizerImpl()
        self.creer_controles_visualisation()

    def afficher_automate(self, automate: Automate) -> None:
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", automate.afficher())
        self.visualizer.dessiner_automate(automate)

    def creer_controles_visualisation(self) -> None:
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(padx=10, pady=5)
        ctk.CTkButton(self.controls_frame, text="Effacer", command=lambda: self.text_area.delete("1.0", "end")).pack(side="left", padx=5)
        ctk.CTkButton(self.controls_frame, text="Exporter Image", command=self.exporter_image_button).pack(side="left", padx=5)

    def exporter_image_button(self):
        try:
            self.visualizer.sauvegarder_image("automate.ps")
            self.text_area.insert("end", "\nImage exportée avec succès.\n")
        except Exception as e:
            self.text_area.insert("end", f"\nErreur lors de l'exportation: {e}\n")

    def integrer_visualiseur(self, type_visualiseur: str) -> None:
        if type_visualiseur.lower() == "turtle":
            self.visualizer = TurtleVisualizerImpl()
        else:
            self.text_area.insert("end", f"\nVisualiseur {type_visualiseur} non supporté.")

    def mode_animation(self, activer: bool) -> None:
        self.text_area.insert("end", f"\nMode animation {'activé' if activer else 'désactivé'}.\n")

    def mode_comparaison(self, automates: List[Automate]) -> None:
        self.text_area.delete("1.0", "end")
        for i, automate in enumerate(automates, 1):
            self.text_area.insert("end", f"\nAutomate {i}:\n{automate.afficher()}\n")

    def afficher_automate_texte(self, automate: Automate) -> None:
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", automate.afficher())

    def afficher_automate_graphique(self, automate: Automate) -> None:
        self.visualizer.dessiner_automate(automate)

    def afficher_resultat_reconnaissance(self, mot: str, resultat: bool) -> None:
        self.text_area.insert("end", f"\nMot '{mot}': {'✓' if resultat else '✗'}\n")

    def afficher_proprietes(self, est_deterministe: bool, est_complet: bool) -> None:
        self.text_area.insert("end", f"Déterministe: {est_deterministe}\nComplet: {est_complet}\n")

    def afficher_matrice(self, matrice: List[List[Set]], etats: List[str], alphabet: List[str]) -> None:
        self.text_area.insert("end", f"États: {etats}\nAlphabet: {alphabet}\n")
        for i, etat in enumerate(etats):
            for j, symbole in enumerate(alphabet):
                if matrice[i][j]:
                    dest_noms = [etats[k] for k in matrice[i][j]]
                    self.text_area.insert("end", f"  {etat} --{symbole}--> {dest_noms}\n")

    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        self.visualizer.animer_reconnaissance(automate, mot)

    def animer_determinisation(self, automate: 'AND') -> None:
        self.visualizer.animer_determinisation(automate)

    def exporter_image(self, nom_fichier: str) -> None:
        self.visualizer.sauvegarder_image(nom_fichier)