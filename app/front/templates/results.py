from dominate.tags import *
from dominate.util import raw
from .base import render_base_page
from Automate import Automate

def render_result_page(automate: Automate, message: str):
    def content():
        with div(_class="flex-1"):
            with div(_class="bg-white p-4 rounded-lg shadow-md animate-fade-in"):
                h2("Résultat", _class="text-lg font-semibold mb-2")
                p(message, id="result-message", _class="mb-4")
                a("Retour à l'accueil", href="/", _class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-300")
            with div(_class="mt-4 bg-white p-4 rounded-lg shadow-md"):
                h2("Description de l'Automate", _class="text-lg font-semibold mb-2")
                with div(_class="space-y-2"):
                    p(raw(f"<strong>Alphabet :</strong> {', '.join(automate.alphabet)}"))
                    p(raw(f"<strong>États :</strong> {', '.join(e.nom for e in automate.etats)}"))
                    p(raw(f"<strong>État initial :</strong> {automate.etat_initial.nom}"))
                    p(raw(f"<strong>États finaux :</strong> {', '.join(e.nom for e in automate.etats_finaux)}"))
                    p(raw(f"<strong>Déterministe :</strong> {'Oui' if automate.est_deterministe() else 'Non'}"))
                    p(raw(f"<strong>Complet :</strong> {'Oui' if automate.est_complet() else 'Non'}"))
        script(raw("""
            document.addEventListener('DOMContentLoaded', () => {
                document.getElementById('modal').classList.add('show');
                document.getElementById('modal-content').textContent = document.getElementById('result-message').textContent;
            });
        """))

    return render_base_page("Résultat", content)