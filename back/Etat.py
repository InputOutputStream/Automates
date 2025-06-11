from typing import Set, Dict, List, Tuple, Optional, Union, Any



class Etat:
    """
    Classe représentant un état dans un automate avec ses propriétés.
    """
    
    def __init__(self, nom: str, est_initial = False, est_final = False) -> None:
        """
        Initialise un état.
        
        Args:
            nom: Nom de l'état
            suivant: etat(s) suivant ou sucesseurs de l'état courrant
            transitions: valeures des transitions
        """
        self.nom = nom
        self.est_initial = est_initial
        self.est_final = est_final
        
    
    def est_accessible(self) -> bool:
        """Vérifie si l'état est accessible depuis l'état initial."""
        pass
    
    def est_utile(self) -> bool:
        """Vérifie si l'état est utile (accessible et coaccessible)."""
        pass
    
    def est_coaccessible(self) -> bool:
        """Vérifie si l'état est coaccessible (peut atteindre un état final)."""
        pass
    
    def chemin_vers_initial(self) -> Optional[List[str]]:
        """Retourne un chemin vers l'état initial s'il existe."""
        pass
    
    def chemin_vers_final(self) -> Optional[List[str]]:
        """Retourne un chemin vers un état final s'il existe."""
        pass
    
    def etats_atteignables(self) -> Set[str]:
        """Retourne l'ensemble des états atteignables depuis cet état."""
        pass
    
    def etats_precedents(self) -> Set[str]:
        """Retourne l'ensemble des états qui peuvent atteindre cet état."""
        pass
    
    def est_emonde(self) -> bool:
        """Vérifie si l'état fait partie de l'automate émondé."""
        pass

    """Surcharge d'operateur"""
    def __str__(self):
        return self.nom
    
    def __repr__(self):
        return f"Etat('{self.nom}')"
    
    def __eq__(self, other):
        return isinstance(other, Etat) and self.nom == other.nom
    
    def __hash__(self):
        return hash(self.nom)
