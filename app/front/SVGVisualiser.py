from typing import Dict, Tuple
import math

from ..Automate import Automate, AND
from ..Etat import Etat
from .AutomateVisualizer import AutomateVisualizer


class SVGVisualizer(AutomateVisualizer):
    """
    Visualiseur générant du SVG statique
    """
    
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        """Initialise le visualiseur SVG"""
        super().__init__(canvas_width, canvas_height)
        self.rayon_etat = 30
        self.espacement_etats = 120
    
    def generer_svg_automate(self, automate: Automate) -> str:
        """Génère le code SVG complet pour l'automate"""
        positions = self.calculer_positions_etats(automate)
        
        svg_elements = []
        svg_elements.append(f'<svg width="{self.canvas_width}" height="{self.canvas_height}" xmlns="http://www.w3.org/2000/svg">')
        
        # Définitions pour les marqueurs de flèches
        svg_elements.append('''
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                    refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="black" />
            </marker>
            <marker id="arrowhead-active" markerWidth="10" markerHeight="7" 
                    refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="red" />
            </marker>
        </defs>
        ''')
        
        # Dessiner les transitions d'abord (pour qu'elles soient sous les états)
        for etat_source in automate.transitions:
            for symbole in automate.transitions[etat_source]:
                for etat_dest in automate.transitions[etat_source][symbole]:
                    svg_elements.append(self.generer_svg_transition(etat_source, etat_dest, symbole, positions))
        
        # Dessiner les états
        for etat in automate.etats:
            x, y = positions[etat]
            couleur = "lightgreen" if etat.est_final else "lightblue"
            if etat.est_initial:
                couleur = "gold"
            svg_elements.append(self.generer_svg_etat(etat, x, y, couleur))
        
        svg_elements.append('</svg>')
        return '\n'.join(svg_elements)
    
    def generer_svg_etat(self, etat: Etat, x: int, y: int, couleur: str = "lightblue") -> str:
        """Génère SVG pour un état"""
        svg_etat = []
        
        # Cercle principal
        svg_etat.append(f'<circle cx="{x}" cy="{y}" r="{self.rayon_etat}" '
                       f'fill="{couleur}" stroke="black" stroke-width="2" '
                       f'id="etat_{etat.nom}" class="etat-circle"/>')
        
        # Cercle double pour état final
        if etat.est_final:
            svg_etat.append(f'<circle cx="{x}" cy="{y}" r="{self.rayon_etat - 5}" '
                           f'fill="none" stroke="black" stroke-width="2"/>')
        
        # Flèche d'entrée pour état initial
        if etat.est_initial:
            start_x = x - self.rayon_etat - 30
            svg_etat.append(f'<line x1="{start_x}" y1="{y}" x2="{x - self.rayon_etat}" y2="{y}" '
                           f'stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>')
        
        # Texte du nom de l'état
        svg_etat.append(f'<text x="{x}" y="{y + 5}" text-anchor="middle" '
                       f'font-family="Arial" font-size="14" fill="black">{etat.nom}</text>')
        
        return '\n'.join(svg_etat)
    
    def generer_svg_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str, positions: Dict) -> str:
        """Génère SVG pour une transition"""
        x1, y1 = positions[etat_source]
        x2, y2 = positions[etat_dest]
        
        if etat_source == etat_dest:
            # Boucle sur soi-même
            loop_x = x1 + self.rayon_etat + 20
            loop_y = y1 - self.rayon_etat - 20
            return f'''
            <path d="M {x1 + self.rayon_etat} {y1} 
                     Q {loop_x} {loop_y} {x1} {y1 - self.rayon_etat}" 
                  fill="none" stroke="black" stroke-width="2" 
                  marker-end="url(#arrowhead)" 
                  id="transition_{etat_source.nom}_{symbole}_{etat_dest.nom}" 
                  class="transition-path"/>
            <text x="{loop_x}" y="{loop_y - 10}" text-anchor="middle" 
                  font-family="Arial" font-size="12" fill="blue">{symbole}</text>
            '''
        else:
            # Transition normale
            # Calculer les points sur les cercles
            angle = math.atan2(y2 - y1, x2 - x1)
            start_x = x1 + self.rayon_etat * math.cos(angle)
            start_y = y1 + self.rayon_etat * math.sin(angle)
            end_x = x2 - self.rayon_etat * math.cos(angle)
            end_y = y2 - self.rayon_etat * math.sin(angle)
            
            # Position du texte au milieu
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2 - 10
            
            return f'''
            <line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" 
                  stroke="black" stroke-width="2" marker-end="url(#arrowhead)" 
                  id="transition_{etat_source.nom}_{symbole}_{etat_dest.nom}" 
                  class="transition-path"/>
            <text x="{mid_x}" y="{mid_y}" text-anchor="middle" 
                  font-family="Arial" font-size="12" fill="blue">{symbole}</text>
            '''
    
    def generer_canvas_html(self, automate: Automate) -> str:
        """Retourne le SVG dans un conteneur HTML"""
        svg_content = self.generer_svg_automate(automate)
        return f'<div class="svg-container">{svg_content}</div>'
    
    def generer_js_animation_reconnaissance(self, automate: Automate, mot: str) -> str:
        """Génère JS pour colorer les états pendant la reconnaissance"""
        return f'''
        function animerReconnaissance(mot) {{
            const etats = document.querySelectorAll('.etat-circle');
            const transitions = document.querySelectorAll('.transition-path');
            
            // Reset colors
            etats.forEach(e => e.style.fill = e.getAttribute('fill'));
            transitions.forEach(t => t.style.stroke = 'black');
            
            let etatCourant = '{automate.etat_initial.nom}';
            let index = 0;
            
            function animer() {{
                if (index >= mot.length) {{
                    // Vérifier si l'état final est acceptant
                    const etatFinal = document.getElementById('etat_' + etatCourant);
                    if (etatFinal) {{
                        etatFinal.style.fill = 'lightgreen';
                    }}
                    return;
                }}
                
                const symbole = mot[index];
                const etatElement = document.getElementById('etat_' + etatCourant);
                const transitionElement = document.getElementById('transition_' + etatCourant + '_' + symbole + '_*');
                
                if (etatElement) {{
                    etatElement.style.fill = 'orange';
                }}
                
                if (transitionElement) {{
                    transitionElement.style.stroke = 'red';
                    transitionElement.style.strokeWidth = '3';
                }}
                
                // Continuer l'animation
                setTimeout(() => {{
                    index++;
                    animer();
                }}, 1000);
            }}
            
            animer();
        }}
        '''
    
    def generer_js_animation_determinisation(self, and_automate: AND) -> str:
        """Génère JS pour montrer la construction des sous-ensembles"""
        return '''
        function animerDeterminisation() {
            // Animation de la construction par sous-ensembles
            console.log("Animation de déterminisation démarrée");
            // TODO: Implémenter l'animation step-by-step
        }
        '''
    
    def generer_css_styles(self) -> str:
        """Styles CSS pour les éléments SVG"""
        return '''
        .svg-container {
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: white;
            overflow: auto;
        }
        
        .etat-circle {
            cursor: pointer;
            transition: fill 0.3s ease;
        }
        
        .etat-circle:hover {
            stroke-width: 3;
        }
        
        .transition-path {
            cursor: pointer;
            transition: stroke 0.3s ease, stroke-width 0.3s ease;
        }
        
        .transition-path:hover {
            stroke: red;
            stroke-width: 3;
        }
        '''
    
    def calculer_positions_etats(self, automate: Automate) -> Dict[Etat, Tuple[int, int]]:
        """Algorithme de positionnement automatique"""
        positions = {}
        etats_list = list(automate.etats)
        n = len(etats_list)
        
        if n == 1:
            positions[etats_list[0]] = (self.canvas_width // 2, self.canvas_height // 2)
        elif n == 2:
            positions[etats_list[0]] = (self.canvas_width // 3, self.canvas_height // 2)
            positions[etats_list[1]] = (2 * self.canvas_width // 3, self.canvas_height // 2)
        else:
            # Positionnement circulaire
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            radius = min(center_x, center_y) - self.margin - self.rayon_etat
            
            for i, etat in enumerate(etats_list):
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[etat] = (int(x), int(y))
        
        return positions

