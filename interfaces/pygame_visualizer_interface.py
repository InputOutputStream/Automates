from abc import ABC, abstractmethod
from typing import Dict, Any
from back.Automate import Automate
from back.Etat import Etat
from automate_visualizer_interface import AutomateVisualizer

class PygameVisualizer(AutomateVisualizer):
    """Interface pour le visualiseur utilisant Pygame."""
    
    @abstractmethod
    def dessiner_automate(self, automate: Automate) -> None:
        """Dessine l'automate avec Pygame."""
        pass
    
    @abstractmethod
    def dessiner_etat(self, etat: Etat, x: int, y: int, couleur: str) -> None:
        """Dessine un état avec Pygame."""
        pass
    
    @abstractmethod
    def dessiner_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str) -> None:
        """Dessine une transition avec Pygame."""
        pass
    
    @abstractmethod
    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        """Animation fluide avec Pygame."""
        pass
    
    @abstractmethod
    def animer_determinisation(self, and_automate: 'AND') -> None:
        """Animation de déterminisation."""
        pass
    
    @abstractmethod
    def gerer_evenements(self) -> Dict[str, Any]:
        """Gère les événements Pygame (clic, drag, etc.)."""
        pass
    
    @abstractmethod
    def mode_edition_interactif(self) -> None:
        """Mode pour créer des automates par drag&drop."""
        pass
    
    @abstractmethod
    def effacer_canvas(self) -> None:
        """Efface la surface Pygame."""
        pass
    
    @abstractmethod
    def sauvegarder_image(self, nom_fichier: str) -> None:
        """Sauvegarde en PNG/JPEG."""
        pass