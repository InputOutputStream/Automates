from typing import Optional
from ..Automate import Automate
from html import escape

from typing import Optional
from .AutomateVisualizer import AutomateVisualizer
 
class ZoneVisualisationHTML:
    """
    Générateur de la zone de visualisation en HTML
    """
    
    def __init__(self, visualiseur: 'AutomateVisualizer'):
        """Initialise avec un visualiseur"""
        self.visualiseur = visualiseur
    
    def generer_conteneur_visualisation(self) -> str:
        """Génère le conteneur principal"""
        return """
        <div id="visualisation-container" class="w-full h-[600px] bg-white rounded-lg shadow-lg p-4">
            <div id="canvas-principal" class="w-full h-3/4"></div>
            <div id="controles-visualisation" class="w-full h-1/4 flex justify-center items-center"></div>
        </div>
        """
    
    def generer_controles_visualisation(self) -> str:
        """Génère les contrôles (zoom, pan, mode)"""
        return """
        <div class="flex gap-4">
            <button id="zoom-in" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Zoom +</button>
            <button id="zoom-out" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Zoom -</button>
            <button id="reset-view" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Réinitialiser</button>
            <select id="mode-visualisation" class="border rounded px-2 py-1">
                <option value="standard">Standard</option>
                <option value="comparaison">Comparaison</option>
            </select>
        </div>
        """
    
    def generer_canvas_principal(self, automate: Optional[Automate] = None) -> str:
        """Génère la zone de dessin principale"""
        nodes = []
        edges = []
        if automate:
            for etat in automate.etats:
                nodes.append(f"{{id: '{escape(str(etat))}', label: '{escape(str(etat))}', shape: 'circle', color: {{background: '{('#00ff00' if etat.est_initial else '#ff0000' if etat.est_final else '#ffffff')}', border: '#000000'}}}}")
            for source, trans in automate.transitions.items():
                for symbole, destinations in trans.items():
                    for dest in destinations:
                        edges.append(f"{{from: '{escape(str(source))}', to: '{escape(str(dest))}', label: '{escape(symbole)}'}}")
        
        nodes_str = "[" + ",".join(nodes) + "]" if nodes else "[]"
        edges_str = "[" + ",".join(edges) + "]" if edges else "[]"
        
        return f"""
        <div id="canvas-principal-vis" class="w-full h-full"></div>
        <script>
            const nodes = new vis.DataSet({nodes_str});
            const edges = new vis.DataSet({edges_str});
            const container = document.getElementById('canvas-principal-vis');
            const data = {{nodes: nodes, edges: edges}};
            const options = {{nodes: {{font: {{size: 16}}}}, edges: {{font: {{size: 14}}, arrows: 'to'}}}};
            const network = new vis.Network(container, data, options);
        </script>
        """
    
    def generer_canvas_comparaison(self, auto1: Automate, auto2: Automate) -> str:
        """Génère deux canvas pour comparaison"""
        canvas1 = self.generer_canvas_principal(auto1).replace("canvas-principal-vis", "canvas-comparaison-1")
        canvas2 = self.generer_canvas_principal(auto2).replace("canvas-principal-vis", "canvas-comparaison-2")
        return f"""
        <div class="flex w-full h-full gap-4">
            <div class="w-1/2 h-full">{canvas1}</div>
            <div class="w-1/2 h-full">{canvas2}</div>
        </div>
        """
    
    def generer_barre_animation(self) -> str:
        """Génère les contrôles d'animation"""
        return """
        <div id="animation-controls" class="flex gap-4 mt-2">
            <button id="play-animation" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">Play</button>
            <button id="pause-animation" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Pause</button>
            <button id="step-animation" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Step</button>
        </div>
        """
    
    def generer_js_controles(self) -> str:
        """JavaScript pour les contrôles interactifs"""
        return """
        document.getElementById('zoom-in').addEventListener('click', () => network.moveTo({scale: network.getScale() * 1.1}));
        document.getElementById('zoom-out').addEventListener('click', () => network.moveTo({scale: network.getScale() / 1.1}));
        document.getElementById('reset-view').addEventListener('click', () => network.fit());
        document.getElementById('mode-visualisation').addEventListener('change', (e) => {
            const mode = e.target.value;
            document.getElementById('canvas-principal').style.display = mode === 'standard' ? 'block' : 'none';
            document.getElementById('canvas-comparaison-1').style.display = mode === 'comparaison' ? 'block' : 'none';
            document.getElementById('canvas-comparaison-2').style.display = mode === 'comparaison' ? 'block' : 'none';
        });
        """
