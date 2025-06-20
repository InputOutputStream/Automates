
from typing import Dict, Any
from .GestionnaireOperations import GestionnaireOperations
import json


class APIHandler:
    """
    Gestionnaire des requêtes API pour l'interface web
    """
    
    def __init__(self, gestionnaire_operations: GestionnaireOperations):
        """Initialise avec le gestionnaire d'opérations"""
        self.gestionnaire = gestionnaire_operations
    
    def traiter_requete_regex(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête de conversion regex"""
        try:
            automate = self.gestionnaire.regex_vers_automate(donnees["regex"])
            return self.gestionnaire.generer_donnees_json(automate)
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def traiter_requete_transformation(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête de transformation d'automate"""
        try:
            automate = self.gestionnaire.generer_donnees_json(donnees["automate"])
            result = self.gestionnaire.endpoint_transformer_automate(donnees["automate"], donnees["operation"])
            return json.loads(result)
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def traiter_requete_test_mot(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête de test de mot"""
        try:
            result = self.gestionnaire.endpoint_tester_mot(donnees["automate"], donnees["mot"])
            return json.loads(result)
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def traiter_requete_comparaison(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête de comparaison d'automates"""
        try:
            auto1 = self.gestionnaire.generer_donnees_json(donnees["auto1"])
            auto2 = self.gestionnaire.generer_donnees_json(donnees["auto2"])
            return {"equivalence": self.gestionnaire.tester_equivalence(auto1, auto2)}
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def traiter_requete_export(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête d'export"""
        try:
            automate = self.gestionnaire.generer_donnees_json(donnees["automate"])
            format = donnees["format"]
            nom_fichier = donnees.get("nom_fichier", "automate")
            if format == "json":
                self.gestionnaire.sauvegarder_json(automate, f"{nom_fichier}.json")
            elif format == "dot":
                self.gestionnaire.sauvegarder_dot(automate, f"{nom_fichier}.dot")
            elif format == "latex":
                self.gestionnaire.exporter_latex(automate, f"{nom_fichier}.tex")
            return {"status": "success", "file": f"{nom_fichier}.{format}"}
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def traiter_requete_import(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête d'import"""
        try:
            automate = self.gestionnaire.charger_json(donnees["file"])
            return self.gestionnaire.generer_donnees_json(automate)
        except Exception as e:
            return self.generer_reponse_erreur(e)
    
    def generer_reponse_erreur(self, erreur: Exception) -> Dict[str, Any]:
        """Génère une réponse d'erreur formatée"""
        return {"error": str(erreur)}
