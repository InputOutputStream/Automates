from abc import ABC, abstractmethod
from typing import Dict, Any

class ParametresApplication(ABC):
    """Interface pour gérer les paramètres de l'application."""
    
    @abstractmethod
    def charger_parametres(self) -> Dict[str, Any]:
        """Charge les paramètres depuis le fichier."""
        pass
    
    @abstractmethod
    def sauvegarder_parametres(self, parametres: Dict[str, Any]) -> None:
        """Sauvegarde les paramètres."""
        pass
    
    @abstractmethod
    def parametres_visualisation(self) -> Dict[str, Any]:
        """Paramètres de visualisation."""
        pass
    
    @abstractmethod
    def parametres_couleurs(self) -> Dict[str, str]:
        """Paramètres de couleurs."""
        pass
    
    @abstractmethod
    def parametres_animations(self) -> Dict[str, Any]:
        """Paramètres d'animations."""
        pass