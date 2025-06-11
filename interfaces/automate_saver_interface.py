from abc import ABC, abstractmethod
from typing import List
from Automate import Automate

class AutomateSaver(ABC):
    """Interface pour sauvegarder/charger des automates."""
    
    @abstractmethod
    def sauvegarder_json(self, automate: Automate, nom_fichier: str) -> None:
        """Sauvegarde en JSON."""
        pass
    
    @abstractmethod
    def charger_json(self, nom_fichier: str) -> Automate:
        """Charge depuis JSON."""
        pass
    
    @abstractmethod
    def sauvegarder_dot(self, automate: Automate, nom_fichier: str) -> None:
        """Sauvegarde au format DOT (Graphviz)."""
        pass
    
    @abstractmethod
    def exporter_latex(self, automate: Automate, nom_fichier: str) -> None:
        """Exporte pour LaTeX (TikZ)."""
        pass
    
    @abstractmethod
    def importer_depuis_matrice(self, matrice: List[List], etats: List[str], 
                               alphabet: List[str]) -> Automate:
        """Importe depuis une matrice de transitions."""
        pass