    
from typing import List
from .ZoneVisualisationHTML import ZoneVisualisationHTML
from .ZoneResultatsHTML import ZoneResultatsHTML
from .ServeurLocal import ServeurLocal
from html import escape


class InterfaceWeb:
    """
    Classe principale de l'interface web
    """
    
    def __init__(self, port: int = 8080):
        """Initialise l'interface web complète"""
        self.port = port
        self.serveur = ServeurLocal(port)
        self.visualisation = ZoneVisualisationHTML(None)
        self.resultats = ZoneResultatsHTML()
    
    def initialiser_composants(self) -> None:
        """Initialise tous les composants"""
        self.serveur.demarrer_serveur()
    
    def generer_page_principale(self) -> str:
        """Génère la page HTML principale"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automate Visualizer</title>
            <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.0/standalone/dist/vis-network.min.js"></script>
            <link href="https://cdn.tailwindcss.com/3.4.1" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100">
            {self.generer_navbar()}
            <div class="container mx-auto p-4">
                {self.generer_layout_responsive()}
            </div>
            {self.generer_footer()}
            {self.generer_modales()}
            {self.generer_css_global()}
            {self.generer_js_global()}
        </body>
        </html>
        """
    
    def generer_layout_responsive(self) -> str:
        """Génère un layout responsive avec Bootstrap"""
        return f"""
        <div class="row">
            <div class="col-md-8">{self.visualisation.generer_conteneur_visualisation()}</div>
            <div class="col-md-4">{self.resultats.generer_onglets_resultats()}</div>
        </div>
        """
    
    def generer_navbar(self) -> str:
        """Génère la barre de navigation"""
        return f"""
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">Automate Visualizer</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item"><a class="nav-link" href="#">Accueil</a></li>
                        <li class="nav-item"><a class="nav-link" href="#import">Importer</a></li>
                        <li class="nav-item"><a class="nav-link" href="#export">Exporter</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        """
    
    def generer_sidebar(self) -> str:
        """Génère la sidebar avec les outils"""
        return f"""
        <div class="col-md-3 bg-light p-3">
            <h4>Outils</h4>
            <button class="btn btn-primary mb-2 w-100">Déterminiser</button>
            <button class="btn btn-primary mb-2 w-100">Minimiser</button>
            <button class="btn btn-primary mb-2 w-100">Compléter</button>
            <button class="btn btn-primary mb-2 w-100">Complémenter</button>
        </div>
        """
    
    def generer_footer(self) -> str:
        """Génère le footer"""
        return f"""
        <footer class="bg-dark text-white text-center p-3 mt-4">
            <p>&copy; 2025 Automate Visualizer</p>
        </footer>
        """
    
    def generer_modales(self) -> List[str]:
        """Génère les fenêtres modales (aide, import/export, etc.)"""
        return [f"""
        <div class="modal fade" id="importModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Importer</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="file" id="import-file" class="form-control">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="importer()">Importer</button>
                    </div>
                </div>
            </div>
        </div>
        """, f"""
        <div class="modal fade" id="exportModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Exporter</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <select id="export-format" class="form-control">
                            <option value="json">JSON</option>
                            <option value="dot">DOT</option>
                            <option value="latex">LaTeX</option>
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="exporter()">Exporter</button>
                    </div>
                </div>
            </div>
        </div>
        """]
    
    def generer_css_global(self) -> str:
        """Génère tous les styles CSS"""
        return """
        <style>
            body { font-family: Arial, sans-serif; }
            .highlight { background-color: yellow !important; }
        </style>
        """
    
    def generer_js_global(self) -> str:
        """Génère tout le JavaScript"""
        return f"""
        <script>
            {self.visualisation.generer_js_controles()}
            {self.resultats.generer_js_onglets()}
        </script>
        """
    
    def lancer_interface(self) -> None:
        """Lance l'interface web"""
        self.initialiser_composants()
        self.serveur.ouvrir_navigateur()
    
    def fermer_interface(self) -> None:
        """Ferme proprement l'interface"""
        self.serveur.arreter_serveur()
