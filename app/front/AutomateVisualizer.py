from ..Automate import Automate

class AutomateVisualizer:
    """Visualiseur d'automates pour l'interface web."""
    
    def __init__(self):
        self.automate = None
        self.positions = {}  # Positions des états pour l'affichage
    
    def set_automate(self, automate: Automate):
        """Définit l'automate à visualiser."""
        self.automate = automate
        self._calculer_positions()
    
    def _calculer_positions(self):
        """Calcule les positions des états pour l'affichage."""
        if not self.automate:
            return
        
        import math
        etats = list(self.automate.etats)
        n = len(etats)
        
        # Disposition circulaire
        for i, etat in enumerate(etats):
            angle = 2 * math.pi * i / n
            x = 300 + 200 * math.cos(angle)
            y = 300 + 200 * math.sin(angle)
            self.positions[etat] = (x, y)
    
    def generer_svg(self) -> str:
        """Génère le code SVG pour la visualisation."""
        if not self.automate:
            return "<svg></svg>"
        
        svg_parts = ['<svg width="600" height="600" xmlns="http://www.w3.org/2000/svg">']
        
        # Dessiner les transitions
        for etat_source, transitions in self.automate.transitions.items():
            x1, y1 = self.positions[etat_source]
            
            for symbole, destinations in transitions.items():
                for etat_dest in destinations:
                    x2, y2 = self.positions[etat_dest]
                    
                    # Ligne de transition
                    svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                                   f'stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>')
                    
                    # Label de transition
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    svg_parts.append(f'<text x="{mx}" y="{my}" text-anchor="middle" '
                                   f'font-family="Arial" font-size="12">{symbole}</text>')
        
        # Dessiner les états
        for etat in self.automate.etats:
            x, y = self.positions[etat]
            
            # Cercle de l'état
            couleur = "lightblue" if etat.est_initial else "white"
            if etat.est_final:
                # Double cercle pour les états finaux
                svg_parts.append(f'<circle cx="{x}" cy="{y}" r="25" fill="{couleur}" '
                               f'stroke="black" stroke-width="2"/>')
                svg_parts.append(f'<circle cx="{x}" cy="{y}" r="20" fill="none" '
                               f'stroke="black" stroke-width="1"/>')
            else:
                svg_parts.append(f'<circle cx="{x}" cy="{y}" r="25" fill="{couleur}" '
                               f'stroke="black" stroke-width="2"/>')
            
            # Nom de l'état
            svg_parts.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" '
                           f'font-family="Arial" font-size="12">{etat.nom}</text>')
        
        # Définir la flèche
        svg_parts.insert(1, '''
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                    refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
            </marker>
        </defs>
        ''')
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

