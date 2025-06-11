from abc import ABC, abstractmethod
from typing import Dict, Tuple
from back.Automate import Automate
from back.Etat import Etat

class AutomateVisualizer(ABC):
    """Interface pour la visualisation d'automates."""
    
    @abstractmethod
    def dessiner_automate(self, automate: Automate) -> None:
        """Dessine un automate sur le canvas."""
        pass
    
    @abstractmethod
    def dessiner_etat(self, etat: Etat, x: int, y: int, couleur: str) -> None:
        """Dessine un état à la position donnée."""
        pass
    
    @abstractmethod
    def dessiner_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str) -> None:
        """Dessine une transition entre deux états."""
        pass
    
    @abstractmethod
    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        """Anime la reconnaissance d'un mot."""
        pass
    
    @abstractmethod
    def animer_determinisation(self, and_automate: 'AND') -> None:
        """Anime le processus de déterminisation."""
        pass
    
    @abstractmethod
    def effacer_canvas(self) -> None:
        """Efface le canvas."""
        pass
    
    @abstractmethod
    def sauvegarder_image(self, nom_fichier: str) -> None:
        """Sauvegarde l'image de l'automate."""
        pass