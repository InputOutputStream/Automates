from flask import Flask, request, render_template_string, send_from_directory, jsonify
from dominate import document
from dominate.tags import *
from dominate.util import raw
from Automate import Automate
from Etat import Etat
from Mot import Mot
import os
import json
from front.templates.main import render_main_page
from front.templates.results import render_result_page

app = Flask(__name__, static_folder="front/static")

# Exemple d'automate
q0 = Etat("q0", est_initial=True)
q1 = Etat("q1", est_final=True)
q2 = Etat("q2")
automate = Automate(
    alphabet={'a', 'b'},
    etats={q0, q1, q2},
    etat_initial=q0,
    etats_finaux={q1}
)
automate.ajouter_transition(q0, 'a', q1)
automate.ajouter_transition(q0, 'b', q0)
automate.ajouter_transition(q1, 'a', q1)
automate.ajouter_transition(q1, 'b', q0)

# Route principale
@app.route('/')
def index():
    return render_template_string(render_main_page(automate))

# Route pour servir le favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('front/static', 'favicon.ico')

# Route pour tester un mot
@app.route('/test', methods=['POST'])
def test_mot():
    mot = request.form.get('mot', '')
    try:
        mot_obj = Mot(mot, automate.alphabet)
        resultat = automate.reconnaitre_mot(mot)
        message = f"Le mot '{mot}' est {'accepté' if resultat else 'rejeté'}."
    except ValueError as e:
        message = f"Erreur : {str(e)}"
    return render_template_string(render_result_page(automate, message))

# Route pour ajouter une transition
@app.route('/add_transition', methods=['POST'])
def add_transition():
    source = request.form.get('source')
    symbole = request.form.get('symbole')
    destination = request.form.get('destination')
    try:
        source_etat = next(e for e in automate.etats if e.nom == source)
        dest_etat = next(e for e in automate.etats if e.nom == destination)
        if symbole in automate.alphabet:
            automate.ajouter_transition(source_etat, symbole, dest_etat)
            message = f"Transition {source} --{symbole}--> {destination} ajoutée."
        else:
            message = f"Erreur : Symbole '{symbole}' n'est pas dans l'alphabet."
    except StopIteration:
        message = "Erreur : État source ou destination invalide."
    except Exception as e:
        message = f"Erreur : {str(e)}"
    return render_template_string(render_result_page(automate, message))

# Route pour ajouter un état
@app.route('/add_etat', methods=['POST'])
def add_etat():
    nom = request.form.get('etat')
    try:
        if nom and nom not in [e.nom for e in automate.etats]:
            new_etat = Etat(nom)
            automate.etats.add(new_etat)
            message = f"État {nom} ajouté."
        else:
            message = "Erreur : Nom d'état invalide ou déjà existant."
    except Exception as e:
        message = f"Erreur : {str(e)}"
    return render_template_string(render_result_page(automate, message))

# Route pour exporter en JSON
@app.route('/export', methods=['POST'])
def export_json():
    data = {
        'alphabet': list(automate.alphabet),
        'etats': [e.nom for e in automate.etats],
        'etat_initial': automate.etat_initial.nom,
        'etats_finaux': [e.nom for e in automate.etats_finaux],
        'transitions': [
            {'source': src.nom, 'symbole': sym, 'destination': dest.nom}
            for src in automate.transitions
            for sym, dests in automate.transitions[src].items()
            for dest in dests
        ]
    }
    with open('automate_export.json', 'w') as f:
        json.dump(data, f, indent=2)
    message = "Automate exporté en JSON (automate_export.json)."
    return render_template_string(render_result_page(automate, message))

# Route pour obtenir la trace de reconnaissance
@app.route('/api/trace_mot', methods=['POST'])
def trace_mot():
    mot = request.json.get('mot', '')
    try:
        mot_obj = Mot(mot, automate.alphabet)
        path = []
        current = automate.etat_initial
        path.append({'state': current.nom})
        for sym in mot:
            if current in automate.transitions and sym in automate.transitions[current]:
                current = next(iter(automate.transitions[current][sym]))
                path.append({'state': current.nom, 'symbol': sym})
            else:
                return jsonify({'error': 'Transition invalide pour ' + sym}), 400
        accepte = current in automate.etats_finaux
        return jsonify({'path': path, 'accepte': accepte})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)