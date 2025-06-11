from abc import ABC, abstractmethod
from Automate import Automate, ADC, AFDC, AND

class GestionnaireOperations(ABC):
    """Interface pour les opérations sur les automates."""
    
    @abstractmethod
    def regex_vers_automate(self, regex: str) -> Automate:
        """Convertit regex en automate."""
        pass
    
    @abstractmethod
    def determiniser_automate(self, automate: AND) -> ADC:
        """Déterminise un automate."""
        pass
    
    @abstractmethod
    def minimiser_automate(self, automate: AFDC) -> AFDC:
        """Minimise un automate."""
        pass
    
    @abstractmethod
    def completer_automate(self, automate: Automate) -> ADC:
        """Complète un automate."""
        pass
    
    @abstractmethod
    def complementaire_automate(self, automate: AFDC) -> AFDC:
        """Calcule le complémentaire."""
        pass
    
    @abstractmethod
    def union_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Union de deux automates."""
        pass
    
    @abstractmethod
    def intersection_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Intersection de deux automates."""
        pass
    
    @abstractmethod
    def concatenation_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Concaténation de deux automates."""
        pass
    
    @abstractmethod
    def etoile_automate(self, automate: Automate) -> Automate:
        """Étoile de Kleene d'un automate."""
        pass
    
    @abstractmethod
    def tester_mot(self, automate: Automate, mot: str) -> bool:
        """Test de reconnaissance d'un mot."""
        pass
    
    @abstractmethod
    def tester_equivalence(self, auto1: Automate, auto2: Automate) -> bool:
        """Test d'équivalence."""
        pass