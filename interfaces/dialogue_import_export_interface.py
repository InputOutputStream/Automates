from abc import ABC, abstractmethod
import customtkinter as ctk
from back.Automate import Automate

class DialogueImportExport(ctk.CTkToplevel, ABC):
    """Interface pour le dialogue d'import/export."""
    
    @abstractmethod
    def importer(self, type_fichier: str) -> Automate:
        """Importe depuis un fichier."""
        pass
    
    @abstractmethod
    def exporter(self, automate: Automate, type_fichier: str) -> None:
        """Exporte vers un fichier."""
        pass
    
    @abstractmethod
    def previsualiser_export(self, automate: Automate, format_export: str) -> str:
        """Prévisualise l'export."""
        pass