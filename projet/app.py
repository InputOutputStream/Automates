from flask import Flask, request, send_from_directory
from generate_page import build_interface
from AND import AND

app = Flask(__name__)

@app.route('/')
def home():
    return build_interface()

@app.route('/recognize', methods=['POST'])
def recognize():
    mot = request.form['mot']
    
    auto = {
        1: {"a": {2, 3}},
        2: {"b": 3},
        3: {"a": 2, "b": 2}
    }
    automate = AND({"a", "b"}, {1, 2, 3}, 1, {3}, auto)
    resultat = automate.reconnaitre_mot(mot, 1)
    
    return f"<p>Résultat : {'Mot reconnu' if resultat else 'Mot non reconnu'}</p>"

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True)
