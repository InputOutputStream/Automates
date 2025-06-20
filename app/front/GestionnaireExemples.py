
from typing import Dict
from ..Automate import Automate, AND, AFNS, Etat


class GestionnaireExemples:
    """
    Gestionnaire d'exemples prédéfinis
    """
    
    def __init__(self):
        """Initialise avec des exemples"""
        self.exemples_automates = {}
        self.exemples_regex = {"(a|b)*": "(a|b)*"}
    
    def charger_exemples_regex(self) -> Dict[str, str]:
        """Charge les exemples de regex"""
        return self.exemples_regex
    
    def charger_exemples_automates(self) -> Dict[str, Automate]:
        """Charge les exemples d'automates"""
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        automate = Automate({"a", "b"}, {q1}, {q0, q1}, q0)
        automate.ajouter_transition(q0, "a", q1)
        automate.ajouter_transition(q0, "b", q0)
        automate.ajouter_transition(q1, "a", q1)
        automate.ajouter_transition(q1, "b", q0)
        self.exemples_automates["simple"] = automate
        return self.exemples_automates
    
    def exemple_automate_simple(self) -> Automate:
        """Exemple d'automate simple"""
        return self.exemples_automates["simple"]
    
    def exemple_automate_non_deterministe(self) -> AND:
        """Exemple d'automate non déterministe"""
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1")
        q2 = Etat("q2", est_final=True)
        automate = AND({"a", "b"}, {q0, q1, q2}, q0, {q2})
        automate.ajouter_transition(q0, "a", q1)
        automate.ajouter_transition(q0, "a", q2)
        automate.ajouter_transition(q1, "b", q2)
        return automate
    
    def exemple_automate_epsilon(self) -> AFNS:
        """Exemple avec epsilon-transitions"""
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        automate = AFNS({"a"}, {q0, q1}, q0, {q1})
        automate.ajouter_transition_epsilon(q0, q1)
        automate.ajouter_transition(q0, "a", q1)
        return automate
    
    def exemple_regex_complexe(self) -> str:
        """Exemple de regex complexe"""
        return "(a|b)*abb"
    
    def generer_selecteur_html(self) -> str:
        """Génère le sélecteur HTML des exemples"""
        options = [f"<option value='{k}'>{k}</option>" for k in self.exemples_automates.keys()]
        return f"""
        <select id="exemple-selector" class="border rounded px-2 py-1">
            {''.join(options)}
        </select>
        """
    
    def generer_js_chargement_exemples(self) -> str:
        """Génère JS pour charger les exemples"""
        return """
        document.getElementById('exemple-selector').addEventListener('change', (e) => {
            fetch('/api/exemple/' + e.target.value)
                .then(response => response.json())
                .then(data => {
                    const nodes = new vis.DataSet(data.nodes);
                    const edges = new vis.DataSet(data.edges);
                    const container = document.getElementById('canvas-principal-vis');
                    const network = new vis.Network(container, {nodes, edges}, options);
                });
        });
        """
