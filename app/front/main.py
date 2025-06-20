"""
Interface Web pour la manipulation des Automates
Structure de base avec génération HTML/CSS/JS via Dominate
"""

from typing import Dict, Callable
from .InterfaceWeb import InterfaceWeb
from .GestionnaireOperations import GestionnaireOperations
from .APIHandler import APIHandler
from .ServeurLocal import ServeurLocal

class Application:
    """
    Classe principale de l'application web
    """
    
    def __init__(self, port: int = 8080, mode_debug: bool = False):
        """Initialise l'application complète"""
        self.port = port
        self.mode_debug = mode_debug
        self.gestionnaire = GestionnaireOperations()
        self.interface = InterfaceWeb(port)
        self.api_handler = APIHandler(self.gestionnaire)
        self.serveur = ServeurLocal(port=self.port)
    
    def initialiser_serveur(self) -> None:
        """Initialise le serveur web"""
        self.interface.initialiser_composants()
    
    def initialiser_gestionnaires(self) -> None:
        """Initialise tous les gestionnaires"""
        self.gestionnaire = GestionnaireOperations()
        self.api_handler = APIHandler(self.gestionnaire)
    
    def generer_application_complete(self) -> None:
        """Génère l'application web complète"""
        with open("index.html", "w") as f:
            f.write(self.interface.generer_page_principale())
    
    def configurer_routes(self) -> Dict[str, Callable]:
        """Configure toutes les routes"""
        return self.serveur.generer_api_endpoints()
    
    def lancer_application(self) -> None:
        """Lance l'application web"""
        self.generer_application_complete()
        self.initialiser_serveur()
        self.interface.lancer_interface()
    
    def fermer_application(self) -> None:
        """Ferme proprement l'application"""
        self.interface.fermer_interface()
    
    def gerer_erreurs_globales(self, erreur: Exception) -> str:
        """Gère les erreurs globales"""
        return self.api_handler.generer_reponse_erreur(erreur)
    
    def generer_page_erreur(self, code_erreur: int, message: str) -> str:
        """Génère une page d'erreur HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erreur {code_erreur}</title>
            <link href="https://cdn.tailwindcss.com/3.4.1" rel="stylesheet">
        </head>
        <body class="p-4">
            <h1>Erreur {code_erreur}</h1>
            <p>{message}</p>
        </body>
        </html>
        """


# Point d'entrée
def main():
    """
    Point d'entrée principal
    """
    # Configuration de l'application
    app = Application(port=8080, mode_debug=True)
    
    # Génération de l'interface
    app.generer_application_complete()
    
    # Lancement du serveur
    app.lancer_application()
    
    print("Interface web disponible sur http://localhost:8080")
    print("Appuyez sur Ctrl+C pour arrêter")


if __name__ == "__main__":
    main()