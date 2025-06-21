
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from typing import Dict, Callable
import webbrowser

from .GestionnaireOperations import GestionnaireOperations
from ..Automate import Automate
from ..Etat import Etat


class ServeurLocal:
    """
    Serveur HTTP local pour servir l'interface web
    """
    
    def __init__(self, port: int = 8080):
        """Initialise le serveur local"""
        self.port = port
        self.gestionnaire = GestionnaireOperations()
        self.server = None
    
    def demarrer_serveur(self) -> None:
        """Démarre le serveur HTTP"""
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    with open("index.html", "rb") as f:
                        self.wfile.write(f.read())
            
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                try:
                    if self.path == "/api/regex":
                        result = self.server.gestionnaire.endpoint_convertir_regex(data.get("regex", ""))
                    elif self.path == "/api/transformer":
                        result = self.server.gestionnaire.endpoint_transformer_automate(data.get("automate", ""), data.get("operation", ""))
                    elif self.path == "/api/tester":
                        result = self.server.gestionnaire.endpoint_tester_mot(data.get("automate", ""), data.get("mot", ""))
                    else:
                        self.send_response(404)
                        self.end_headers()
                        return
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        
        Handler.gestionnaire = self.gestionnaire
        self.server = HTTPServer(('', self.port), Handler)
        self.server.serve_forever()
    
    def arreter_serveur(self) -> None:
        """Arrête le serveur"""
        if self.server:
            self.server.server_close()
    
    def generer_api_endpoints(self) -> Dict[str, Callable]:
        """Génère les endpoints API REST"""
        return {
            "/api/regex": self.endpoint_convertir_regex,
            "/api/transformer": self.endpoint_transformer_automate,
            "/api/tester": self.endpoint_tester_mot
        }
    
    def endpoint_convertir_regex(self, regex: str) -> str:
        """Endpoint pour conversion regex -> automate"""
        automate = self.gestionnaire.regex_vers_automate(regex)
        return self.gestionnaire.generer_donnees_json(automate)
    
    def endpoint_transformer_automate(self, automate_json: str, operation: str) -> str:
        """Endpoint pour transformations d'automates"""
        data = json.loads(automate_json)
        etats = {Etat(e) for e in data["etats"]}
        etat_initial = Etat(data["etat_initial"], est_initial=True)
        etats_finaux = {Etat(e, est_final=True) for e in data["etats_finaux"]}
        automate = Automate(set(data["alphabet"]), etats, etat_initial, etats_finaux)
        for t in data["transitions"]:
            automate.ajouter_transition(Etat(t["source"]), t["symbole"], Etat(t["destination"]))
        
        if operation == "determiniser":
            result = self.gestionnaire.determiniser_automate(automate)
        elif operation == "minimiser":
            result = self.gestionnaire.minimiser_automate(automate)
        elif operation == "completer":
            result = self.gestionnaire.completer_automate(automate)
        elif operation == "complementaire":
            result = self.gestionnaire.complementaire_automate(automate)
        else:
            raise ValueError("Opération non supportée")
        
        return self.gestionnaire.generer_donnees_json(result)
    
    def endpoint_tester_mot(self, automate_json: str, mot: str) -> str:
        """Endpoint pour test de reconnaissance"""
        data = json.loads(automate_json)
        etats = {Etat(e) for e in data["etats"]}
        etat_initial = Etat(data["etat_initial"], est_initial=True)
        etats_finaux = {Etat(e, est_final=True) for e in data["etats_finaux"]}
        automate = Automate(set(data["alphabet"]), etats, etat_initial, etats_finaux)
        for t in data["transitions"]:
            automate.ajouter_transition(Etat(t["source"]), t["symbole"], Etat(t["destination"]))
        return json.dumps({"result": self.gestionnaire.tester_mot(automate, mot)})
    
    def ouvrir_navigateur(self) -> None:
        """Ouvre l'interface dans le navigateur"""
        webbrowser.open(f"http://localhost:{self.port}")
