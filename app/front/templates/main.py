from dominate.tags import *
from dominate.util import raw
from .base import render_base_page
from Automate import Automate

def render_main_page(automate: Automate):
    def content():
        # Sidebar
        with aside(_class="w-64 bg-gray-200 p-4 rounded-lg shadow-md mr-4"):
            h2("Actions", _class="text-lg font-semibold mb-4")
            # Add Etat
            with div(_class="bg-white p-4 rounded-lg shadow-md mb-4"):
                h3("Ajouter un État", _class="text-md font-semibold mb-2")
                with form(method="POST", action="/add_etat", _class="space-y-2"):
                    input_(type="text", name="etat", placeholder="Nouvel état (ex: q3)", _class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300")
                    button("Ajouter", type="submit", _class="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition duration-300")
            # Add Transition
            with div(_class="bg-white p-4 rounded-lg shadow-md mb-4"):
                h3("Ajouter une Transition", _class="text-md font-semibold mb-2")
                with form(method="POST", action="/add_transition", _class="space-y-2"):
                    input_(type="text", name="source", placeholder="État source (ex: q0)", _class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300")
                    input_(type="text", name="symbole", placeholder="Symbole (ex: a)", _class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300")
                    input_(type="text", name="destination", placeholder="État destination (ex: q1)", _class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300")
                    button("Ajouter", type="submit", _class="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition duration-300")
            # Export
            with div(_class="bg-white p-4 rounded-lg shadow-md"):
                h3("Exporter", _class="text-md font-semibold mb-2")
                with form(method="POST", action="/export", _class="space-y-2"):
                    button("Exporter en JSON", type="submit", _class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-300")

        # Main content
        with div(_class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4"):
            # Graph
            with div(_class="bg-white p-4 rounded-lg shadow-md"):
                h2("Visualisation de l'Automate", _class="text-lg font-semibold mb-2")
                div(id="automate-graph", _class="w-full h-96")
                script(raw(f"""
                    document.addEventListener('DOMContentLoaded', () => {{
                        const elements = [
                            {','.join(f"{{data: {{id: '{e.nom}', label: '{e.nom}', isInitial: {str(e.nom == automate.etat_initial.nom).lower()}, isFinal: {str(e.nom in [f.nom for f in automate.etats_finaux]).lower()}}}}}" for e in automate.etats)},
                            {','.join(f"{{data: {{id: '{src.nom}-{sym}-{dest.nom}', source: '{src.nom}', target: '{dest.nom}', label: '{sym}'}}}}" for src in automate.transitions for sym, dests in automate.transitions[src].items() for dest in dests)}
                        ];
                        const cy = cytoscape({{
                            container: document.getElementById('automate-graph'),
                            elements,
                            style: [
                                {{
                                    selector: 'node',
                                    style: {{
                                        'background-color': '#60a5fa',
                                        'label': 'data(label)',
                                        'shape': 'circle',
                                        'width': 50,
                                        'height': 50,
                                        'text-valign': 'center',
                                        'color': '#fff',
                                        'border-width': node => node.data('isFinal') ? 3 : 1,
                                        'border-color': node => node.data('isFinal') ? '#ef4444' : '#000',
                                        'font-size': 12
                                    }}
                                }},
                                {{
                                    selector: 'edge',
                                    style: {{
                                        'width': 2,
                                        'line-color': '#4b5563',
                                        'target-arrow-color': '#4b5563',
                                        'target-arrow-shape': 'triangle',
                                        'curve-style': 'bezier',
                                        'label': 'data(label)',
                                        'font-size': 10,
                                        'text-rotation': 'autorotate'
                                    }}
                                }},
                                {{
                                    selector: 'node[isInitial]',
                                    style: {{
                                        'background-color': '#22c55e'
                                    }}
                                }},
                                {{
                                    selector: '.highlight',
                                    style: {{
                                        'background-color': '#f59e0b',
                                        'line-color': '#f59e0b'
                                    }}
                                }}
                            ],
                            layout: {{
                                name: 'cose',
                                animate: true,
                                animationDuration: 500
                            }}
                        }});
                        window.cy = cy; // Expose pour animation
                    }});
                """))

            # Input and Results
            with div():
                with div(_class="bg-white p-4 rounded-lg shadow-md mb-4"):
                    h2("Tester un Mot", _class="text-lg font-semibold mb-2")
                    with form(_class="flex space-x-2", onsubmit="animateRecognition(this.mot.value); return true;", method="POST", action="/test"):
                        input_(type="text", name="mot", placeholder="Entrez un mot (ex: aba)", _class="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300")
                        button("Tester", type="submit", _class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-300")

                with div(_class="bg-white p-4 rounded-lg shadow-md"):
                    h2("Propriétés de l'Automate", _class="text-lg font-semibold mb-2")
                    with div(_class="space-y-2"):
                        p(raw(f"<strong>Alphabet :</strong> {', '.join(automate.alphabet)}"))
                        p(raw(f"<strong>États :</strong> {', '.join(e.nom for e in automate.etats)}"))
                        p(raw(f"<strong>État initial :</strong> {automate.etat_initial.nom}"))
                        p(raw(f"<strong>États finaux :</strong> {', '.join(e.nom for e in automate.etats_finaux)}"))
                        p(raw(f"<strong>Déterministe :</strong> {'Oui' if automate.est_deterministe() else 'Non'}"))
                        p(raw(f"<strong>Complet :</strong> {'Oui' if automate.est_complet() else 'Non'}"))

    return render_base_page("Démonstration d'Automate", content)