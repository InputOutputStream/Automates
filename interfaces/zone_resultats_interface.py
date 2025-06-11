from abc import ABC, abstractmethod
from typing import Dict
import customtkinter as ctk
from back.Automate import Automate

class ZoneResultats(ctk.CTkFrame, ABC):
    """Interface pour la zone d'affichage des résultats."""
    
    @abstractmethod
    def creer_onglets_resultats(self) -> None:
        """Crée les onglets (propriétés, tests, transformations)."""
        pass
    
    @abstractmethod
    def afficher_proprietes_automate(self, automate: Automate) -> None:
        """Affiche les propriétés de l'automate."""
        pass
    
    @abstractmethod
    def afficher_resultats_tests(self, resultats: Dict[str, bool]) -> None:
        """Affiche les résultats des tests de mots."""
        pass
    
    @abstractmethod
    def afficher_transformations(self, transformations: Dict[str, Automate]) -> None:
        """Affiche les automates transformés."""
        pass
    
    @abstractmethod
    def afficher_historique(self) -> None:
        """Affiche l'historique des opérations."""
        pass
    
    @abstractmethod
    def exporter_resultats(self, format_export: str) -> None:
        """Exporte les résultats."""
        pass