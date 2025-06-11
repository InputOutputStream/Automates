from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any

#Import
import itertools
from Automate import Automate,ADC

class AND(Automate):
    """
    Automate Non Déterministe.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux automates non déterministes.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, etats_finaux: Set[str]) -> None:
        """Initialise un AND."""
        super().__init__(alphabet,etats,etat_initial,etats_finaux)
        pass
    
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition non déterministe."""
        pass
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition non déterministe."""
        pass
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne un ensemble d'états (non déterminisme)."""
        pass
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance non déterministe d'un mot."""
        pass
    
    def est_deterministe(self) -> bool:
        """Vérifie le déterminisme."""
        pass
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        
        pass
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        pass
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        pass
