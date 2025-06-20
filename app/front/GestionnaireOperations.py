

from itertools import product
import json
from ..Automate import AFND, AFNS, Automate, ADC, AFDC, AND, Etat


class GestionnaireOperations:
    """
    Gestionnaire des opérations sur les automates (logique métier inchangée)
    """
    
    def __init__(self):
        """Initialise le gestionnaire"""
        self.operations_history = []
    
    def regex_vers_automate(self, regex: str) -> Automate:
        """Convertit regex en automate"""
        # Simplification : accepte (a|b)*
        if regex == "(a|b)*":
            q0 = Etat("q0", est_initial=True, est_final=True)
            automate = AFND({"a", "b"}, {q0}, q0, {q0})
            automate.ajouter_transition(q0, "a", q0)
            automate.ajouter_transition(q0, "b", q0)
            return automate
        raise NotImplementedError("Regex complexe non supporté")
    
    def determiniser_automate(self, automate: AND) -> ADC:
        """Déterminise un automate"""
        self.operations_history.append("Déterminisation")
        return automate.determiniser()
    
    def minimiser_automate(self, automate: AFDC) -> AFDC:
        """Minimise un automate"""
        self.operations_history.append("Minimisation")
        return automate.minimiser()
    
    def completer_automate(self, automate: Automate) -> ADC:
        """Complète un automate"""
        self.operations_history.append("Complétion")
        if isinstance(automate, ADC):
            return automate
        adc = ADC(automate.alphabet, automate.etats, automate.etat_initial, automate.etats_finaux)
        adc.transitions = automate.transitions.copy()
        adc.completer()
        return adc
    
    def complementaire_automate(self, automate: AFDC) -> AFDC:
        """Calcule le complémentaire"""
        self.operations_history.append("Complémentation")
        return automate.complementaire()
    
    def union_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Union de deux automates"""
        self.operations_history.append("Union")
        nouveaux_etats = {Etat(f"{e.nom}_1") for e in auto1.etats} | {Etat(f"{e.nom}_2") for e in auto2.etats}
        q0 = Etat("q0", est_initial=True)
        nouveaux_etats.add(q0)
        nouveaux_finaux = {Etat(f"{e.nom}_1") for e in auto1.etats_finaux} | {Etat(f"{e.nom}_2") for e in auto2.etats_finaux}
        automate = AND(auto1.alphabet | auto2.alphabet, nouveaux_etats, q0, nouveaux_finaux)
        for e in auto1.etats:
            if e in auto1.transitions:
                for s, ds in auto1.transitions[e].items():
                    for d in ds:
                        automate.ajouter_transition(Etat(f"{e.nom}_1"), s, Etat(f"{d.nom}_1"))
        for e in auto2.etats:
            if e in auto2.transitions:
                for s, ds in auto2.transitions[e].items():
                    for d in ds:
                        automate.ajouter_transition(Etat(f"{auto1.etat_initial.nom}_1"), "", Etat(f"{auto2.etat_initial.nom}_2"))        
        
        return automate
    
    def intersection_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Intersection de deux automates"""
        self.operations_history.append("Intersection")
        nouveaux_etats = {Etat(f"{e1.nom}_{e2.nom}") for e1, e2 in product(auto1.etats, auto2.etats)}
        q0 = Etat("q0", est_initial=True)
        nouveaux_finaux = {Etat(f"{e.nom}_1") for e in auto1.etats_finaux if e in auto2.etats_finaux}
        automate = AND(auto1.alphabet | auto2.alphabet, nouveaux_etats, q0, nouveaux_finaux)
        for e in auto1.etats:
            if e in auto1.transitions:
                for s, ds in auto1.transitions[e].items():
                    for d in ds:
                        if Etat(f"{d.nom}_2") in auto2.etats:
                            automate.ajouter_transition(Etat(f"{e.nom}_1"), s, Etat(f"{d.nom}_2"))
        for e in auto2.etats:
            if e in auto2.transitions:
                for s, ds in auto2.transitions[e].items():
                    for d in ds:
                        if Etat(f"{d.nom}_1") in auto1.etats:
                            automate.ajouter_transition(Etat(f"{e.nom}_2"), s, Etat(f"{d.nom}_1"))
        return automate
    
    def concatenation_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Concaténation de deux automates"""
        self.operations_history.append("Concaténation")
        nouveaux_etats = auto1.etats | auto2.etats
        q0 = Etat("q0", est_initial=True)
        nouveaux_etats.add(q0)
        nouveaux_finaux = auto2.etats_finaux
        automate = AND(auto1.alphabet | auto2.alphabet, nouveaux_etats, q0, nouveaux_finaux)
        for e in auto1.etats:
            if e in auto1.transitions:
                for s, ds in auto1.transitions[e].items():
                    for d in ds:
                        automate.ajouter_transition(Etat(e.nom), s, Etat(d.nom))
        for e in auto1.etats_finaux:
            for s in auto2.alphabet:
                automate.ajouter_transition(Etat(e.nom), s, auto2.etat_initial)
        return automate
    
    def etoile_automate(self, automate: Automate) -> Automate:
        """Étoile de Kleene d'un automate"""
        self.operations_history.append("Étoile de Kleene")
        nouveaux_etats = automate.etats.copy()
        q0 = Etat("q0", est_initial=True, est_final=True)
        nouveaux_etats.add(q0)
        automate_resultat = AFNS(automate.alphabet | {""}, nouveaux_etats, q0, {q0} | automate.etats_finaux)
        for e in automate.etats:
            if e in automate.transitions:
                for s, ds in automate.transitions[e].items():
                    for d in ds:
                        automate_resultat.ajouter_transition(Etat(e.nom), s, Etat(d.nom))
        for e in automate.etats_finaux:
            automate_resultat.ajouter_transition_epsilon(e, q0)
        return automate_resultat
    
    def tester_mot(self, automate: Automate, mot: str) -> bool:
        """Test de reconnaissance d'un mot"""
        self.operations_history.append(f"Test du mot {mot}")
        return automate.reconnaitre_mot(mot)
    
    def tester_equivalence(self, auto1: Automate, auto2: Automate) -> bool:
        """Test d'équivalence"""
        self.operations_history.append("Test d'équivalence")
        auto1_min = self.minimiser_automate(auto1.determiniser()) if isinstance(auto1, AND) else auto1
        auto2_min = self.minimiser_automate(auto2.determiniser()) if isinstance(auto2, AND) else auto2
        return auto1_min.etats == auto2_min.etats and auto1_min.transitions == auto2_min.transitions
    
    def generer_donnees_json(self, automate: Automate) -> str:
    
        """Génère les données JSON pour le frontend"""
        data = {
            "alphabet": list(automate.alphabet),
            "etats": [str(e) for e in automate.etats],
            "etat_initial": str(automate.etat_initial),
            "etats_finaux": [str(e) for e in automate.etats_finaux],
            "transitions": [
                {"source": str(s), "symbole": sym, "destination": str(d)}
                for s, trans in automate.transitions.items()
                for sym, dests in trans.items()
                for d in dests
            ]
        }

        return json.dumps(data)
