from interfaces.application_interface import Application
from .main_window import MainWindowImpl
import customtkinter as ctk

class ApplicationImpl(Application):
    def __init__(self):
        self.main_window = MainWindowImpl()
        self.connecter_evenements()

    def initialiser_composants(self) -> None:
        self.main_window.initialiser_interface()

    def connecter_evenements(self) -> None:
        def test_automate():
            try:
                automate = self.main_window.zone_saisie.get_automate_saisi()
                self.main_window.zone_visualisation.afficher_automate(automate)
                for mot in self.main_window.zone_saisie.get_mots_test():
                    result = automate.reconnaitre_mot(mot)
                    self.main_window.zone_visualisation.afficher_resultat_reconnaissance(mot, result)
                self.main_window.zone_resultats.afficher_proprietes_automate(automate)
            except Exception as e:
                self.main_window.afficher_erreur(str(e))

        self.main_window.zone_saisie.button.configure(command=test_automate)

    def lancer_application(self) -> None:
        self.main_window.mainloop()

    def fermer_application(self) -> None:
        self.main_window.destroy()

    def gerer_erreurs(self, erreur: Exception) -> None:
        self.main_window.afficher_erreur(str(erreur))