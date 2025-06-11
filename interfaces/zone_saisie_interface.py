from abc import ABC, abstractmethod
from typing import Tuple
import customtkinter as ctk

class ZoneSaisie(ctk.CTkFrame, ABC):
    """Interface pour la zone de saisie des données d'entrée."""
    
    @abstractmethod
    def creer_saisie_regex(self) -> None:
        """Crée la zone de saisie pour regex."""
        pass
    
    @abstractmethod
    def creer_saisie_automate_manuel(self) -> None:
        """Crée la zone pour saisir un automate manuellement."""
        pass
    
    @abstractmethod
    def creer_saisie_mots_test(self) -> None:
        """Crée la zone pour saisir des mots de test."""
        pass
    
    @abstractmethod
    def creer_boutons_action(self) -> None:
        """Crée les boutons d'action."""
        pass
    
    @abstractmethod
    def valider_saisies(self) -> Tuple[bool, str]:
        """Valide toutes les saisies."""
        pass
    
    @abstractmethod
    def effacer_saisies(self) -> None:
        """Efface toutes les saisies."""
        pass
    
    @abstractmethod
    def charger_exemple(self, nom_exemple: str) -> None:
        """Charge un exemple prédéfini."""
        pass