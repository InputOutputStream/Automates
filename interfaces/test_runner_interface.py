from abc import ABC, abstractmethod
from typing import List, Dict
from Automate import Automate

class TestRunner(ABC):
    """Interface pour exécuter des tests sur les automates."""
    
    @abstractmethod
    def tester_mots_liste(self, automate: Automate, mots: List[str]) -> Dict[str, bool]:
        """Teste une liste de mots."""
        pass
    
    @abstractmethod
    def generer_mots_acceptes(self, automate: Automate, longueur_max: int) -> List[str]:
        """Génère tous les mots acceptés jusqu'à une longueur."""
        pass
    
    @abstractmethod
    def generer_mots_refuses(self, automate: Automate, longueur_max: int) -> List[str]:
        """Génère des mots refusés."""
        pass
    
    @abstractmethod
    def test_equivalence_automates(self, auto1: Automate, auto2: Automate) -> bool:
        """Teste l'équivalence de deux automates."""
        pass
    
    @abstractmethod
    def benchmark_reconnaissance(self, automate: Automate, mots: List[str]) -> Dict[str, float]:
        """Mesure les performances."""
        pass