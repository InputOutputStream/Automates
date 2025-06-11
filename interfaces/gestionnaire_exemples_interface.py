from abc import ABC, abstractmethod
from typing import Dict
from Automate import Automate, AND, AFNS

class GestionnaireExemples(ABC):
    """Interface pour le gestionnaire d'exemples prédéfinis."""
    
    @abstractmethod
    def charger_exemples_regex(self) -> Dict[str, str]:
        """Charge les exemples de regex."""
        pass
    
    @abstractmethod
    def charger_exemples_automates(self) -> Dict[str, Automate]:
        """Charge les exemples d'automates."""
        pass
    
    @abstractmethod
    def exemple_automate_simple(self) -> Automate:
        """Exemple d'automate simple."""
        pass
    
    @abstractmethod
    def exemple_automate_non_deterministe(self) -> AND:
        """Exemple d'automate non déterministe."""
        pass
    
    @abstractmethod
    def exemple_automate_epsilon(self) -> AFNS:
        """Exemple avec epsilon-transitions."""
        pass
    
    @abstractmethod
    def exemple_regex_complexe(self) -> str:
        """Exemple de regex complexe."""
        pass