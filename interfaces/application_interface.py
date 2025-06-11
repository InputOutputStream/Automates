from abc import ABC, abstractmethod

class Application(ABC):
    """Interface pour la classe principale de l'application."""
    
    @abstractmethod
    def initialiser_composants(self) -> None:
        """Initialise tous les composants."""
        pass
    
    @abstractmethod
    def connecter_evenements(self) -> None:
        """Connecte tous les événements."""
        pass
    
    @abstractmethod
    def lancer_application(self) -> None:
        """Lance l'application."""
        pass
    
    @abstractmethod
    def fermer_application(self) -> None:
        """Ferme proprement l'application."""
        pass
    
    @abstractmethod
    def gerer_erreurs(self, erreur: Exception) -> None:
        """Gère les erreurs globales."""
        pass