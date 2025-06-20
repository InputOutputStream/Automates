from typing import Dict, Any
import json

# Import des classes métier existantes
from ..Etat import Etat
from ..Automate import Automate
from .GestionnaireOperations import GestionnaireOperations


class AutomateSaver:
    """
    Classe pour sauvegarder/charger des automates (logique métier inchangée)
    """
    
    def __init__(self):
        """Initialise le gestionnaire de fichiers"""
        self.gestionnaire = GestionnaireOperations()
    
    def sauvegarder_json(self, automate: Automate, nom_fichier: str) -> None:
        """Sauvegarde en JSON"""
        with open(nom_fichier, 'w') as f:
            json.dump(self.gestionnaire.generer_donnees_json(automate), f)
    
    def charger_json(self, nom_fichier: str) -> Automate:
        """Charge depuis JSON"""
        with open(nom_fichier, 'r') as f:
            data = json.load(f)
        etats = {Etat(e) for e in data["etats"]}
        etat_initial = Etat(data["etat_initial"], est_initial=True)
        etats_finaux = {Etat(e, est_final=True) for e in data["etats_finaux"]}
        automate = Automate(set(data["alphabet"]), etats, etat_initial, etats_finaux)
        for t in data["transitions"]:
            automate.ajouter_transition(Etat(t["source"]), t["symbole"], Etat(t["destination"]))
        return automate
    
    def sauvegarder_dot(self, automate: Automate, nom_fichier: str) -> None:
        """Sauvegarde au format DOT (Graphviz)"""
        with open(nom_fichier, 'w') as f:
            f.write("digraph G {\n")
            for etat in automate.etats:
                shape = "doublecircle" if etat.est_final else "circle"
                f.write(f'  "{etat}" [shape={shape}];\n')
            if automate.etat_initial:
                f.write(f'  start [shape=point];\n  start -> "{automate.etat_initial}";\n')
            for source, trans in automate.transitions.items():
                for symbole, dests in trans.items():
                    for dest in dests:
                        f.write(f'  "{source}" -> "{dest}" [label="{symbole}"];\n')
            f.write("}\n")
    
    def exporter_latex(self, automate: Automate, nom_fichier: str) -> None:
        """Exporte pour LaTeX (TikZ)"""
        with open(nom_fichier, 'w') as f:
            f.write("""
            \\documentclass{standalone}
            \\usepackage{tikz}
            \\usetikzlibrary{automata,positioning}
            \\begin{document}
            \\begin{tikzpicture}[->,>=stealth,auto,node distance=2cm]
            \\tikzstyle{state}=[circle,draw,minimum size=1cm]
            \\tikzstyle{accepting}=[double circle,draw,minimum size=1cm]
            """)
            for etat in automate.etats:
                style = "accepting" if etat.est_final else "state"
                initial = ",initial" if etat == automate.etat_initial else ""
                f.write(f'\\node[{style}{initial}] ({etat}) at (0,0) {{$q_{{{etat.nom}}}$}};\n')
            for source, trans in automate.transitions.items():
                for symbole, dests in trans.items():
                    for dest in dests:
                        f.write(f'\\path ({source}) edge node {{$\\scriptstyle {symbole}$}} ({dest});\n')
            f.write("\\end{tikzpicture}\n\\end{document}\n")
    
    def exporter_html_interactif(self, automate: Automate, nom_fichier: str) -> None:
        """Exporte une page HTML interactive standalone"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.0/standalone/dist/vis-network.min.js"></script>
            <link href="https://cdn.tailwindcss.com/3.4.1" rel="stylesheet">
        </head>
        <body class="p-4">
            <div id="automate" class="w-full h-[600px] border"></div>
            <script>
                const nodes = new vis.DataSet({self.gestionnaire.generer_donnees_json(automate)["nodes"]});
                const edges = new vis.DataSet({self.gestionnaire.generer_donnees_json(automate)["edges"]});
                const container = document.getElementById('automate');
                const data = {{nodes: nodes, edges: edges}};
                const options = {{nodes: {{font: {{size: 16}}}}, edges: {{font: {{size: 14}}, arrows: 'to'}}}};
                const network = new vis.Network(container, data, options);
            </script>
        </body>
        </html>
        """
        with open(nom_fichier, 'w') as f:
            f.write(html)
    
    def generer_donnees_web(self, automate: Automate) -> Dict[str, Any]:
        """Génère les données formatées pour le web"""
        return json.loads(self.gestionnaire.generer_donnees_json(automate))

