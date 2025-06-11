# front/zone_resultats.py
import customtkinter as ctk
from interfaces.zone_resultats_interface import ZoneResultats
from back.Automate import Automate
from typing import Dict, List

class ZoneResultatsImpl(ZoneResultats):
    def __init__(self, parent):
        super().__init__(parent)
        self.notebook = ctk.CTkTabview(self)
        self.notebook.add("Propriétés")
        self.notebook.add("Tests")
        self.notebook.add("Transformations")
        self.notebook.pack(fill="both", expand=True)
        self.text_proprietes = ctk.CTkTextbox(self.notebook.tab("Propriétés"))
        self.text_tests = ctk.CTkTextbox(self.notebook.tab("Tests"))
        self.text_transformations = ctk.CTkTextbox(self.notebook.tab("Transformations"))
        self.text_proprietes.pack(fill="both", expand=True)
        self.text_tests.pack(fill="both", expand=True)
        self.text_transformations.pack(fill="both", expand=True)

    def creer_onglets_resultats(self) -> None:
        pass

    def afficher_proprietes_automate(self, automate: Automate) -> None:
        self.text_proprietes.delete("1.0", "end")
        self.text_proprietes.insert("1.0", automate.afficher())
        self.text_proprietes.insert("end", f"\nDéterministe: {automate.est_deterministe()}")
        self.text_proprietes.insert("end", f"\nComplet: {automate.est_complet()}")

    def afficher_resultats_tests(self, resultats: Dict[str, bool]) -> None:
        self.text_tests.delete("1.0", "end")
        for mot, resultat in resultats.items():
            self.text_tests.insert("end", f"Mot '{mot}': {'✓' if resultat else '✗'}\n")

    def afficher_transformations(self, transformations: Dict[str, Automate]) -> None:
        self.text_transformations.delete("1.0", "end")
        for nom, automate in transformations.items():
            self.text_transformations.insert("end", f"{nom}:\n{automate.afficher()}\n\n")

    def afficher_historique(self, historique: List[str]) -> None:
        self.text_proprietes.insert("end", "\nHistorique des opérations:\n")
        for op in historique:
            self.text_proprietes.insert("end", f"- {op}\n")

    def exporter_resultats(self, format_export: str, nom_fichier: str) -> None:
        pass