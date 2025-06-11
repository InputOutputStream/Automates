import customtkinter as ctk
from interfaces.main_window_interface import MainWindow
from .zone_saisie import ZoneSaisieImpl
from .zone_visualisation import ZoneVisualisationImpl
from .zone_resultats import ZoneResultatsImpl

class MainWindowImpl(MainWindow):
    def __init__(self):
        super().__init__()
        self.title("Automate Simulator")
        self.geometry("800x600")
        self.initialiser_interface()

    def initialiser_interface(self) -> None:
        self.zone_saisie = ZoneSaisieImpl(self)
        self.zone_visualisation = ZoneVisualisationImpl(self)
        self.zone_resultats = ZoneResultatsImpl(self)
        self.zone_saisie.pack(side="left", fill="y", padx=10, pady=10)
        self.zone_visualisation.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.zone_resultats.pack(side="bottom", fill="x", padx=10, pady=10)

    def creer_menu_principal(self) -> None:
        pass

    def creer_barre_outils(self) -> None:
        pass

    def creer_zones_principales(self) -> None:
        pass

    def afficher_erreur(self, message: str) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Erreur")
        ctk.CTkLabel(dialog, text=message).pack(padx=20, pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)