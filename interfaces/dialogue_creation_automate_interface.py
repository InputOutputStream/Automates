from abc import ABC, abstractmethod
import customtkinter as ctk
from Automate import Automate

class DialogueCreationAutomate(ctk.CTkToplevel, ABC):
    """Interface pour le dialogue de création d'automate."""
    
    @abstractmethod
    def creer_interface_creation(self) -> None:
        """Crée l'interface de création."""
        pass
    
    @abstractmethod
    def ajouter_etat(self) -> None:
        """Ajoute un état."""
        pass
    
    @abstractmethod
    def supprimer_etat(self) -> None:
        """Supprime un état."""
        pass
    
    @abstractmethod
    def ajouter_transition(self) -> None:
        """Ajoute une transition."""
        pass
    
    @abstractmethod
    def supprimer_transition(self) -> None:
        """Supprime une transition."""
        pass
    
    @abstractmethod
    def definir_alphabet(self) -> None:
        """Définit l'alphabet."""
        pass
    
    @abstractmethod
    def valider_automate(self) -> Automate:
        """Valide et retourne l'automate créé."""
        pass