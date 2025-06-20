
from itertools import product
import time
from typing import Dict, List, Any
from ..Automate import Automate
from .GestionnaireOperations import GestionnaireOperations


class TestRunner:
    """
    Classe pour exécuter des tests sur les automates (logique métier inchangée)
    """
    
    def __init__(self):
        """Initialise le testeur"""
        self.gestionnaire = GestionnaireOperations()
    
    def tester_mots_liste(self, automate: Automate, mots: List[str]) -> Dict[str, bool]:
        """Teste une liste de mots"""
        return {mot: automate.reconnaitre_mot(mot) for mot in mots}
    
    def generer_mots_acceptes(self, automate: Automate, longueur_max: int) -> List[str]:
        """Génère tous les mots acceptés jusqu'à une longueur"""
        mots = []
        for length in range(longueur_max + 1):
            for prod in product(automate.alphabet, repeat=length):
                mot = "".join(prod)
                if automate.reconnaitre_mot(mot):
                    mots.append(mot)
        return mots
    
    def generer_mots_refuses(self, automate: Automate, longueur_max: int) -> List[str]:
        """Génère des mots refusés"""
        mots = []
        for length in range(longueur_max + 1):
            for prod in product(automate.alphabet, repeat=length):
                mot = "".join(prod)
                if not automate.reconnaitre_mot(mot):
                    mots.append(mot)
        return mots
    
    def test_equivalence_automates(self, auto1: Automate, auto2: Automate) -> bool:
        """Teste l'équivalence de deux automates"""
        return self.gestionnaire.tester_equivalence(auto1, auto2)
    
    def benchmark_reconnaissance(self, automate: Automate, mots: List[str]) -> Dict[str, float]:
        """Mesure les performances"""
        resultats = {}
        for mot in mots:
            start = time()
            automate.reconnaitre_mot(mot)
            resultats[mot] = time() - start
        return resultats
    
    def generer_rapport_html(self, resultats: Dict[str, Any]) -> str:
        """Génère un rapport HTML des tests"""
        rows = [f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in resultats.items()]
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link href="https://cdn.tailwindcss.com/3.4.1" rel="stylesheet">
        </head>
        <body class="p-4">
            <table class="table table-bordered">
                <tr><th>Mot</th><th>Temps (s)</th></tr>
                {''.join(rows)}
            </table>
        </body>
        </html>
        """
