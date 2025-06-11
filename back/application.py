from interfaces.application_interface import Application
import customtkinter as ctk
from back.Automate import MainWindowImpl

class App(Application):
    def initialiser_composants(self) -> None:
        self.main_window = MainWindowImpl()
        # Initialiser autres composants
    
    def connecter_evenements(self) -> None:
        # Connecter événements
        pass
    
    def lancer_application(self) -> None:
        self.main_window.mainloop()
    
    def fermer_application(self) -> None:
        self.main_window.destroy()
    
    def gerer_erreurs(self, erreur: Exception) -> None:
        # Gérer erreurs
        pass