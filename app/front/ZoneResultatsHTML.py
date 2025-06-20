from typing import Dict
from ..Automate import Automate
from html import escape


class ZoneResultatsHTML:
    """
    Générateur de la zone de résultats en HTML
    """
    
    def __init__(self):
        """Initialise le générateur de résultats"""
        self.resultats = {}
    
    def generer_onglets_resultats(self) -> str:
        """Génère les onglets avec Bootstrap"""
        return """
        <ul class="nav nav-tabs" id="resultats-tabs" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="proprietes-tab" data-bs-toggle="tab" href="#proprietes" role="tab">Propriétés</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="tests-tab" data-bs-toggle="tab" href="#tests" role="tab">Tests</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="transformations-tab" data-bs-toggle="tab" href="#transformations" role="tab">Transformations</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="historique-tab" data-bs-toggle="tab" href="#historique" role="tab">Historique</a>
            </li>
        </ul>
        <div class="tab-content">
            <div class="tab-pane active" id="proprietes" role="tabpanel"></div>
            <div class="tab-pane" id="tests" role="tabpanel"></div>
            <div class="tab-pane" id="transformations" role="tabpanel"></div>
            <div class="tab-pane" id="historique" role="tabpanel"></div>
        </div>
        """
    
    def generer_onglet_proprietes(self, automate: Automate) -> str:
        """Onglet des propriétés de l'automate"""
        return f"""
        <div class="p-4">
            {self.generer_tableau_proprietes(automate)}
        </div>
        """
    
    def generer_onglet_tests(self) -> str:
        """Onglet des résultats de tests"""
        return """
        <div class="p-4">
            <table id="tableau-tests" class="table table-striped"></table>
        </div>
        """
    
    def generer_onglet_transformations(self) -> str:
        """Onglet des automates transformés"""
        return """
        <div class="p-4">
            <div id="transformed-automates" class="grid grid-cols-2 gap-4"></div>
        </div>
        """
    
    def generer_onglet_historique(self) -> str:
        """Onglet de l'historique des opérations"""
        return """
        <div class="p-4">
            <ul id="historique-operations" class="list-group"></ul>
        </div>
        """
    
    def generer_tableau_proprietes(self, automate: Automate) -> str:
        """Génère un tableau des propriétés"""
        return f"""
        <table class="table table-bordered">
            <tr><th>Propriété</th><th>Valeur</th></tr>
            <tr><td>Déterministe</td><td>{'Oui' if automate.est_deterministe() else 'Non'}</td></tr>
            <tr><td>Complet</td><td>{'Oui' if automate.est_complet() else 'Non'}</td></tr>
            <tr><td>Nombre d'états</td><td>{len(automate.etats)}</td></tr>
            <tr><td>Alphabet</td><td>{', '.join(sorted(automate.alphabet))}</td></tr>
        </table>
        """
    
    def generer_tableau_tests(self, resultats: Dict[str, bool]) -> str:
        """Génère le tableau des résultats de tests"""
        rows = [f"<tr><td>{escape(mot)}</td><td>{'Accepté' if res else 'Refusé'}</td></tr>" for mot, res in resultats.items()]
        return f"""
        <table class="table table-bordered">
            <tr><th>Mot</th><th>Résultat</th></tr>
            {''.join(rows)}
        </table>
        """
    
    def generer_js_onglets(self) -> str:
        """JavaScript pour la gestion des onglets"""
        return """
        const tabs = document.querySelectorAll('#resultats-tabs .nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                document.querySelector(tab.getAttribute('href')).classList.add('active');
            });
        });
        """

