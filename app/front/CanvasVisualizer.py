
from typing import Dict, Tuple
import json
import math

# Import des classes métier existantes
from ..Automate import Automate, AND
from ..Etat import Etat
from .AutomateVisualizer import AutomateVisualizer




class CanvasVisualizer(AutomateVisualizer):
    """
    Visualiseur utilisant Canvas HTML5 (plus interactif)
    """
    
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        """Initialise le visualiseur Canvas"""
        super().__init__(canvas_width, canvas_height)
        self.rayon_etat = 30
    
    def generer_svg_automate(self, automate: Automate) -> str:
        """Non utilisé pour Canvas, retourne chaîne vide"""
        return ""
    
    def generer_canvas_html(self, automate: Automate) -> str:
        """Génère l'élément canvas HTML"""
        return f'''
        <canvas id="automateCanvas" width="{self.canvas_width}" height="{self.canvas_height}" 
                style="border: 1px solid #ccc; background-color: white; border-radius: 5px;">
            Votre navigateur ne supporte pas Canvas HTML5.
        </canvas>
        '''
    
    def generer_js_dessin_automate(self, automate: Automate) -> str:
        """Génère JS pour dessiner sur canvas"""
        positions = self.calculer_positions_etats(automate)
        
        js_code = f'''
        const canvas = document.getElementById('automateCanvas');
        const ctx = canvas.getContext('2d');
        
        // Données de l'automate
        const positions = {json.dumps({str(k): v for k, v in positions.items()})};
        const transitions = {json.dumps(self._serialize_transitions(automate))};
        
        function dessinerAutomate() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Dessiner les transitions
            {self._generer_js_transitions(automate)}
            
            // Dessiner les états
            {self._generer_js_etats(automate)}
        }}
        
        dessinerAutomate();
        '''
        
        return js_code
    
    def _serialize_transitions(self, automate: Automate) -> Dict:
        """Sérialise les transitions pour JSON"""
        transitions = {}
        for source in automate.transitions:
            transitions[str(source)] = {}
            for symbole in automate.transitions[source]:
                transitions[str(source)][symbole] = [str(dest) for dest in automate.transitions[source][symbole]]
        return transitions
    
    def _generer_js_etats(self, automate: Automate) -> str:
        """Génère le JS pour dessiner tous les états"""
        js_etats = []
        for etat in automate.etats:
            couleur = "'lightgreen'" if etat.est_final else "'lightblue'"
            if etat.est_initial:
                couleur = "'gold'"
            js_etats.append(f"dessinerEtat('{etat.nom}', {couleur}, {etat.est_final}, {etat.est_initial});")
        
        return '\n'.join(js_etats)
    
    def _generer_js_transitions(self, automate: Automate) -> str:
        """Génère le JS pour dessiner toutes les transitions"""
        js_transitions = []
        for source in automate.transitions:
            for symbole in automate.transitions[source]:
                for dest in automate.transitions[source][symbole]:
                    js_transitions.append(f"dessinerTransition('{source}', '{dest}', '{symbole}');")
        
        return '\n'.join(js_transitions)
    
    def generer_js_dessin_etat(self, etat: Etat, x: int, y: int, couleur: str = "lightblue") -> str:
        """JS pour dessiner un état"""
        return f'''
        function dessinerEtat(nom, couleur, estFinal, estInitial) {{
            const pos = positions[nom];
            const x = pos[0];
            const y = pos[1];
            
            // Cercle principal
            ctx.beginPath();
            ctx.arc(x, y, {self.rayon_etat}, 0, 2 * Math.PI);
            ctx.fillStyle = couleur;
            ctx.fill();
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Cercle double pour état final
            if (estFinal) {{
                ctx.beginPath();
                ctx.arc(x, y, {self.rayon_etat - 5}, 0, 2 * Math.PI);
                ctx.strokeStyle = 'black';
                ctx.lineWidth = 2;
                ctx.stroke();
            }}
            
            // Flèche d'entrée pour état initial
            if (estInitial) {{
                ctx.beginPath();
                ctx.moveTo(x - {self.rayon_etat} - 30, y);
                ctx.lineTo(x - {self.rayon_etat}, y);
                ctx.strokeStyle = 'black';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Pointe de flèche
                ctx.beginPath();
                ctx.moveTo(x - {self.rayon_etat}, y);
                ctx.lineTo(x - {self.rayon_etat} - 10, y - 5);
                ctx.lineTo(x - {self.rayon_etat} - 10, y + 5);
                ctx.closePath();
                ctx.fillStyle = 'black';
                ctx.fill();
            }}
            
            // Texte du nom
            ctx.fillStyle = 'black';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(nom, x, y + 5);
        }}
        '''
    
    def generer_js_dessin_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str) -> str:
        """JS pour dessiner une transition"""
        return f'''
        function dessinerTransition(source, dest, symbole) {{
            const pos1 = positions[source];
            const pos2 = positions[dest];
            const x1 = pos1[0];
            const y1 = pos1[1];
            const x2 = pos2[0];
            const y2 = pos2[1];
            
            if (source === dest) {{
                // Boucle sur soi-même
                const loopX = x1 + {self.rayon_etat} + 20;
                const loopY = y1 - {self.rayon_etat} - 20;
                
                ctx.beginPath();
                ctx.arc(loopX, loopY, 20, 0, 2 * Math.PI);
                ctx.strokeStyle = 'black';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Texte
                ctx.fillStyle = 'blue';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(symbole, loopX, loopY - 30);
            }} else {{
                // Ligne droite avec flèche
                const angle = Math.atan2(y2 - y1, x2 - x1);
                const startX = x1 + {self.rayon_etat} * Math.cos(angle);
                const startY = y1 + {self.rayon_etat} * Math.sin(angle);
                const endX = x2 - {self.rayon_etat} * Math.cos(angle);
                const endY = y2 - {self.rayon_etat} * Math.sin(angle);
                
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.lineTo(endX, endY);
                ctx.strokeStyle = 'black';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Pointe de flèche
                const arrowSize = 10;
                ctx.beginPath();
                ctx.moveTo(endX, endY);
                ctx.lineTo(endX - arrowSize * Math.cos(angle - Math.PI/6), 
                          endY - arrowSize * Math.sin(angle - Math.PI/6));
                ctx.lineTo(endX - arrowSize * Math.cos(angle + Math.PI/6), 
                          endY - arrowSize * Math.sin(angle + Math.PI/6));
                ctx.closePath();
                ctx.fillStyle = 'black';
                ctx.fill();
                
                // Texte au milieu
                const midX = (startX + endX) / 2;
                const midY = (startY + endY) / 2 - 10;
                ctx.fillStyle = 'blue';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(symbole, midX, midY);
            }}
        }}
        '''
    
    def generer_js_animation_reconnaissance(self, automate: Automate, mot: str) -> str:
        """Animation Canvas pour reconnaissance"""
        return f'''
        function animerReconnaissanceCanvas(mot) {{
            let index = 0;
            let etatCourant = '{automate.etat_initial.nom}';
            
            function animer() {{
                dessinerAutomate();
                
                // Highlighter l'état courant
                const pos = positions[etatCourant];
                ctx.beginPath();
                ctx.arc(pos[0], pos[1], {self.rayon_etat}, 0, 2 * Math.PI);
                ctx.strokeStyle = 'red';
                ctx.lineWidth = 4;
                ctx.stroke();
                
                if (index < mot.length) {{
                    setTimeout(() => {{
                        index++;
                        animer();
                    }}, 1000);
                }}
            }}
            
            animer();
        }}
        '''
    
    def generer_js_animation_determinisation(self, and_automate: AND) -> str:
        """Animation Canvas pour déterminisation"""
        return '''
        function animerDeterminisationCanvas() {
            console.log("Animation Canvas de déterminisation");
            // TODO: Implémenter l'animation
        }
        '''
    
    def generer_js_interactivite(self) -> str:
        """JS pour drag&drop et édition interactive"""
        return f'''
        let isDragging = false;
        let dragTarget = null;
        let mousePos = {{ x: 0, y: 0 }};
        
        canvas.addEventListener('mousedown', function(e) {{
            const rect = canvas.getBoundingClientRect();
            mousePos.x = e.clientX - rect.left;
            mousePos.y = e.clientY - rect.top;
            
            // Vérifier si on clique sur un état
            for (let etat in positions) {{
                const pos = positions[etat];
                const distance = Math.sqrt(Math.pow(mousePos.x - pos[0], 2) + Math.pow(mousePos.y - pos[1], 2));
                if (distance <= {self.rayon_etat}) {{
                    isDragging = true;
                    dragTarget = etat;
                    break;
                }}
            }}
        }});
        
        canvas.addEventListener('mousemove', function(e) {{
            if (isDragging && dragTarget) {{
                const rect = canvas.getBoundingClientRect();
                mousePos.x = e.clientX - rect.left;
                mousePos.y = e.clientY - rect.top;
                
                positions[dragTarget] = [mousePos.x, mousePos.y];
                dessinerAutomate();
            }}
        }});
        
        canvas.addEventListener('mouseup', function(e) {{
            isDragging = false;
            dragTarget = null;
        }});
        '''
    
    def generer_css_styles(self) -> str:
        """Styles CSS pour le canvas"""
        return '''
        #automateCanvas {
            cursor: grab;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        #automateCanvas:active {
            cursor: grabbing;
        }
        '''
    
    def calculer_positions_etats(self, automate: Automate) -> Dict[Etat, Tuple[int, int]]:
        """Positions pour canvas"""
        positions = {}
        etats_list = list(automate.etats)
        n = len(etats_list)
        
        if n == 1:
            positions[etats_list[0]] = (self.canvas_width // 2, self.canvas_height // 2)
        elif n <= 4:
            # Disposition en ligne pour peu d'états
            for i, etat in enumerate(etats_list):
                x = (i + 1) * self.canvas_width // (n + 1)
                y = self.canvas_height // 2
                positions[etat] = (x, y)
        else:
            # Disposition circulaire
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            radius = min(center_x, center_y) - self.margin - self.rayon_etat
            
            for i, etat in enumerate(etats_list):
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[etat] = (int(x), int(y))
        
        return positions

