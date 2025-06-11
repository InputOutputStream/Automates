# front/main_window_interface.py
from abc import ABC, abstractmethod
import customtkinter as ctk

class MainWindow(ctk.CTk, ABC):
    """Interface pour la fenêtre principale de l'application."""
    
    @abstractmethod
    def initialiser_interface(self) -> None:
        """Configure l'interface utilisateur avec les zones principales."""
        pass
    
    @abstractmethod
    def creer_menu_principal(self) -> None:
        """Crée la barre de menu avec les options (fichier, édition, etc.)."""
        pass
    
    @abstractmethod
    def creer_barre_outils(self) -> None:
        """Crée la barre d'outils pour les actions rapides."""
        pass
    
    @abstractmethod
    def creer_zones_principales(self) -> None:
        """Crée les zones de saisie, visualisation et résultats."""
        pass
    
    @abstractmethod
    def afficher_erreur(self, message: str) -> None:
        """Affiche un message d'erreur à l'utilisateur."""
        pass