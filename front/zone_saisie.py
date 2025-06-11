import customtkinter as ctk
from interfaces.zone_saisie_interface import ZoneSaisie
from back.Automate import Automate
from back.Etat import Etat
from typing import Tuple, List

class ZoneSaisieImpl(ZoneSaisie):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Test Automate")
        self.label.pack(padx=10, pady=10)
        self.entry_words = ctk.CTkEntry(self, placeholder_text="Mots à tester (séparés par des virgules)")
        self.entry_words.pack(padx=10, pady=5)
        self.button = ctk.CTkButton(self, text="Créer Exemple", command=self.creer_exemple)
        self.button.pack(padx=10, pady=10)
        self.automate = None

    def creer_exemple(self):
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        self.automate = Automate(
            alphabet={'a', 'b'},
            etats={q0, q1},
            etat_initial=q0,
            etats_finaux={q1}
        )
        self.automate.ajouter_transition(q0, 'a', q1)
        self.automate.ajouter_transition(q0, 'b', q0)
        self.automate.ajouter_transition(q1, 'a', q1)
        self.automate.ajouter_transition(q1, 'b', q0)

    def creer_saisie_regex(self) -> None:
        pass

    def creer_saisie_automate_manuel(self) -> None:
        pass

    def creer_saisie_mots_test(self) -> None:
        pass

    def creer_boutons_action(self) -> None:
        pass

    def valider_saisies(self) -> Tuple[bool, str]:
        return self.automate is not None, "Automate créé" if self.automate else "Aucun automate"

    def effacer_saisies(self) -> None:
        self.automate = None

    def charger_exemple(self, nom_exemple: str) -> None:
        pass

    def get_automate_saisi(self) -> Automate:
        if self.automate:
            return self.automate
        raise ValueError("Aucun automate saisi")

    def get_mots_test(self) -> List[str]:
        words = self.entry_words.get().strip()
        return [w.strip() for w in words.split(",") if w.strip()] or ["a", "ba", "bba"]