
import json

from ..Automate import Automate, AFDC, AND
from .GestionnaireOperations import GestionnaireOperations



class JSAnimationGenerator:
    """
    Générateur de code JavaScript pour les animations
    """
    
    def __init__(self):
        """Initialise le générateur d'animations"""
        self.gestionnaire = GestionnaireOperations()
    
    def generer_animation_reconnaissance(self, automate: Automate, mot: str) -> str:
        """Génère JS pour animer la reconnaissance d'un mot"""
        path = []
        current = automate.etat_initial
        path.append(str(current))
        for symbole in mot:
            next_states = automate.obtenir_transitions(current, symbole)
            if next_states:
                current = next(iter(next_states))
                path.append(str(current))
        return f"""
        let step = 0;
        const path = {json.dumps(path)};
        function animate() {{
            if (step < path.length) {{
                document.getElementById('node-' + path[step]).classList.add('highlight');
                setTimeout(() => {{
                    document.getElementById('node-' + path[step]).classList.remove('highlight');
                    step++;
                    animate();
                }}, 1000);
            }}
        }}
        animate();
        """
    
    def generer_animation_determinisation(self, and_automate: AND) -> str:
        """Génère JS pour animer la déterminisation"""
        adc = self.gestionnaire.determiniser_automate(and_automate)
        return f"""
        const adc = {self.gestionnaire.generer_donnees_json(adc)};
        let step = 0;
        function animate() {{
            if (step < adc.nodes.length) {{
                document.getElementById('node-' + adc.nodes[step].id).classList.add('highlight');
                setTimeout(() => {{
                    document.getElementById('node-' + adc.nodes[step].id).classList.remove('highlight');
                    step++;
                    animate();
                }}, 1000);
            }}
        }}
        animate();
        """
    
    def generer_animation_minimisation(self, automate: AFDC) -> str:
        """Génère JS pour animer la minimisation"""
        minimised = self.gestionnaire.minimiser_automate(automate)
        return f"""
        const minimised = {self.gestionnaire.generer_donnees_json(minimised)};
        let step = 0;
        function animate() {{
            if (step < minimised.nodes.length) {{
                document.getElementById('node-' + minimised.nodes[step].id).classList.add('highlight');
                setTimeout(() => {{
                    document.getElementById('node-' + minimised.nodes[step].id).classList.remove('highlight');
                    step++;
                    animate();
                }}, 1000);
            }}
        }}
        animate();
        """
    
    def generer_animation_completion(self, automate: Automate) -> str:
        """Génère JS pour animer la complétion"""
        completed = self.gestionnaire.completer_automate(automate)
        return f"""
        const completed = {self.gestionnaire.generer_donnees_json(completed)};
        let step = 0;
        function animate() {{
            if (step < completed.nodes.length) {{
                document.getElementById('node-' + completed.nodes[step].id).classList.add('highlight');
                setTimeout(() => {{
                    document.getElementById('node-' + completed.nodes[step].id).classList.remove('highlight');
                    step++;
                    animate();
                }}, 1000);
            }}
        }}
        animate();
        """
    
    def generer_transitions_css(self) -> str:
        """Génère les transitions CSS pour les animations"""
        return """
        .highlight {
            background-color: yellow !important;
            transition: background-color 0.5s;
        }
        """
    
    def generer_controles_animation(self) -> str:
        """Génère JS pour play/pause/step"""
        return """
        let isPlaying = false;
        document.getElementById('play-animation').addEventListener('click', () => {
            isPlaying = true;
            animate();
        });
        document.getElementById('pause-animation').addEventListener('click', () => {
            isPlaying = false;
        });
        document.getElementById('step-animation').addEventListener('click', () => {
            if (!isPlaying) {
                animate();
            }
        });
        """
