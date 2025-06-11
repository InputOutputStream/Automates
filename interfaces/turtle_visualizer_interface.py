from abc import ABC, abstractmethod
from typing import Dict, Tuple
from back.Automate import Automate
from back.Etat import Etat
from .automate_visualizer_interface import AutomateVisualizer

class TurtleVisualizer(AutomateVisualizer):
    """Interface pour le visualiseur utilisant Turtle Graphics."""
    
    @abstractmethod
    def dessiner_automate(self, automate: Automate) -> None:
        """Dessine l'automate avec Turtle."""
        pass
    
    @abstractmethod
    def dessiner_etat(self, etat: Etat, x: int, y: int, couleur: str) -> None:
        """Dessine un état circulaire."""
        pass
    
    @abstractmethod
    def dessiner_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str) -> None:
        """Dessine une flèche avec label."""
        pass
    
    @abstractmethod
    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        """Anime étape par étape la reconnaissance."""
        pass
    
    @abstractmethod
    def animer_determinisation(self, and_automate: 'AND') -> None:
        """Anime la construction des sous-ensembles."""
        pass
    
    @abstractmethod
    def calculer_positions_etats(self, automate: Automate) -> Dict[Etat, Tuple[int, int]]:
        """Calcule les positions optimales des états."""
        pass
    
    @abstractmethod
    def effacer_canvas(self) -> None:
        """Efface tout."""
        pass
    
    @abstractmethod
    def sauvegarder_image(self, nom_fichier: str) -> None:
        """Sauvegarde en PostScript."""
        pass