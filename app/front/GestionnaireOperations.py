from itertools import product
import json
from typing import Tuple
import re

from app.front.RegexParser import RegexParser
from ..Automate import AFND, AFNS, Automate, ADC, AFDC, AND, AD, AutomateMinimal, Canonisation
from ..Etat import Etat
from ..LangageReconnaissable import LangageReconnaissable


class GestionnaireOperations:
    """
    Gestionnaire des opérations sur les automates 
    """
    
    def __init__(self):
        """Initialise le gestionnaire"""
        self.operations_history = []
    
    def regex_vers_automate(self, regex: str, type : int = 0) -> Automate:
        """Convertit regex en automate"""
        if type == 1:
            return RegexParser.construire_automate_glushkov(regex)
        elif type == 0:
            return RegexParser.construire_automate_thompson(regex)
        else:
            raise ValueError("Valeur de methode inconnu")
    
    def valider_syntaxe(self, regex):
        print("bug here")
        return RegexParser.valider_syntaxe(regex)
    
    def canoniser_automate(self, automate: Automate):
        """ Canonisation d'un automate """
        return Canonisation.appliquer(automate)

    def determiniser_automate(self, automate: AND, type: int=0) -> AD:
        """Déterminise un automate"""
        self.operations_history.append("Déterminisation")
        return automate.determinisation_thompson()
        
    def minimiser_automate(self, automate: Automate) -> AFDC:
        """Minimise un automate"""
        step1 = AFDC(autre=automate)
        #result = AutomateMinimal(automate_source=step1)
        result = step1.minimiser_optimise()
        self.operations_history.append("Minimisation par fusion")
        return result


    def completer_automate(self, automate: Automate) -> ADC:
        """Complète un automate"""
        self.operations_history.append("Complétion")
        
        # Utilisation du constructeur ADC pour la complétion
        if isinstance(automate, ADC):
            return automate
        
        # Création directe d'un ADC
        return ADC(
            alphabet=automate.alphabet,
            etats=automate.etats,
            etat_initial=automate.etat_initial,
            etats_finaux=automate.etats_finaux
        )

    
    def complementaire_automate(self, automate: AFDC) -> AFDC:
        """Calcule le complémentaire"""
        self.operations_history.append("Complémentation")
        at = AFDC(autre=automate)
        return at.complementaire()
        

    def validate_equations(self, equations: dict) -> Tuple[bool, str]:
        from .ValidateurSystemeEquations import ValidateurSystemeEquations
        validateur = ValidateurSystemeEquations()
        est_valide, message = validateur.validate_equations(equations)
        return est_valide, message
    

    def extract_variables(self, equations):
        """Extrait les variables d'un système d'équations"""
        variables = set()
        for var in equations.keys():
            variables.add(var)
        return sorted(list(variables))
    
    def automaton2reg(self, automaton: Automate):
        """Application du lemme d'arden """
        return LangageReconnaissable.arden_dfa_to_regex(automaton)
    
        
    def eqn2reg(self, equations):
        """Application du lemme d'arden """
        return LangageReconnaissable.appliquer_lemmes_arden(equations)
                

    def union_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Union simplifiée - Évite la duplication de code"""
        self.operations_history.append("Union")
        
        # Helper pour mapper les états
        def map_states(automaton, suffix):
            mapping = {}
            new_states = set()
            for e in automaton.etats:
                new_state = Etat(f"{e.nom}_{suffix}", est_final=e.est_final)
                new_states.add(new_state)
                mapping[e] = new_state
            return mapping, new_states
        
        # Mapper les états des deux automates
        map1, states1 = map_states(auto1, "1")
        map2, states2 = map_states(auto2, "2")
        
        # Nouvel état initial
        q0 = Etat("q0_union", est_initial=True)
        all_states = states1 | states2 | {q0}
        
        # États finaux + q0 si un des initiaux est final
        final_states = {map1[e] for e in auto1.etats_finaux} | {map2[e] for e in auto2.etats_finaux}
        if auto1.etat_initial in auto1.etats_finaux or auto2.etat_initial in auto2.etats_finaux:
            q0.est_final = True
            final_states.add(q0)
        
        # Créer automate et ajouter transitions
        result = AFNS(auto1.alphabet | auto2.alphabet | {""}, all_states, q0, final_states)
        
        # Transitions epsilon vers initiaux
        result.ajouter_transition(q0, "", map1[auto1.etat_initial])
        result.ajouter_transition(q0, "", map2[auto2.etat_initial])
        
        # Copier toutes les transitions
        for auto, mapping in [(auto1, map1), (auto2, map2)]:
            for state, transitions in auto.transitions.items():
                for symbol, destinations in transitions.items():
                    for dest in destinations:
                        result.ajouter_transition(mapping[state], symbol, mapping[dest])
        
        return result


            
    def intersection_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Intersection simplifiée - Une seule version optimisée"""
        self.operations_history.append("Intersection")
        
        alphabet_commun = auto1.alphabet & auto2.alphabet
        if not alphabet_commun:
            empty_state = Etat("vide")
            return AD(set(), {empty_state}, empty_state, set())
        
        # États et mappings
        states, finals, mapping = set(), set(), {}
        queue = [(auto1.etat_initial, auto2.etat_initial)]
        visited = set()
        
        # Helper pour créer un état
        def create_state(e1, e2):
            is_final = e1 in auto1.etats_finaux and e2 in auto2.etats_finaux
            state = Etat(f"({e1.nom},{e2.nom})", est_final=is_final)
            states.add(state)
            mapping[(e1, e2)] = state
            if is_final:
                finals.add(state)
            return state
        
        # État initial
        initial = create_state(*queue[0])
        result = AD(alphabet_commun, states, initial, finals)
        
        # BFS pour construction
        while queue:
            e1, e2 = queue.pop(0)
            if (e1, e2) in visited:
                continue
            visited.add((e1, e2))
            
            source = mapping[(e1, e2)]
            
            for symbol in alphabet_commun:
                dests1 = auto1.transitions.get(e1, {}).get(symbol, set())
                dests2 = auto2.transitions.get(e2, {}).get(symbol, set())
                
                for d1, d2 in product(dests1, dests2):
                    if (d1, d2) not in mapping:
                        create_state(d1, d2)
                        queue.append((d1, d2))
                    
                    result.ajouter_transition(source, symbol, mapping[(d1, d2)])
        
        return result

    
                
    def concatenation_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Concaténation simplifiée"""
        self.operations_history.append("Concaténation")
        
        # Helper pour mapper avec suffixes
        def map_auto(auto, suffix, keep_finals=True):
            mapping = {}
            new_states = set()
            for e in auto.etats:
                new_state = Etat(f"{e.nom}_{suffix}", est_final=e.est_final if keep_finals else False)
                new_states.add(new_state)
                mapping[e] = new_state
            return mapping, new_states
        
        map1, states1 = map_auto(auto1, "1", keep_finals=False)
        map2, states2 = map_auto(auto2, "2", keep_finals=True)
        
        all_states = states1 | states2
        initial = map1[auto1.etat_initial]
        finals = {map2[e] for e in auto2.etats_finaux}
        
        result = AFNS(auto1.alphabet | auto2.alphabet | {""}, all_states, initial, finals)
        
        # Copier transitions et ajouter epsilon-transitions
        for auto, mapping in [(auto1, map1), (auto2, map2)]:
            for state, transitions in auto.transitions.items():
                for symbol, destinations in transitions.items():
                    for dest in destinations:
                        result.ajouter_transition(mapping[state], symbol, mapping[dest])
        
        # Epsilon des finaux de auto1 vers initial de auto2
        for final in auto1.etats_finaux:
            result.ajouter_transition(map1[final], "", map2[auto2.etat_initial])
        
        return result
                
    def etoile_automate(self, automate: Automate) -> Automate:
        """Étoile de Kleene simplifiée"""
        self.operations_history.append("Étoile de Kleene")
        
        # Mapper les états
        mapping = {}
        new_states = set()
        for e in automate.etats:
            new_state = Etat(f"{e.nom}_star", est_final=e.est_final)
            new_states.add(new_state)
            mapping[e] = new_state
        
        # Nouvel état initial (toujours final pour epsilon)
        q0 = Etat("q0_star", est_initial=True, est_final=True)
        new_states.add(q0)
        
        finals = {q0} | {mapping[e] for e in automate.etats_finaux}
        result = AFNS(automate.alphabet | {""}, new_states, q0, finals)
        
        # Epsilon vers ancien initial
        result.ajouter_transition(q0, "", mapping[automate.etat_initial])
        
        # Copier transitions
        for state, transitions in automate.transitions.items():
            for symbol, destinations in transitions.items():
                for dest in destinations:
                    result.ajouter_transition(mapping[state], symbol, mapping[dest])
        
        # Epsilon des finaux vers initial (répétition)
        for final in automate.etats_finaux:
            result.ajouter_transition(mapping[final], "", mapping[automate.etat_initial])
        
        return result
        
    def tester_mot(self, automate: Automate, mot: str) -> bool:
        """Test de reconnaissance d'un mot"""
        self.operations_history.append(f"Test du mot {mot}")
        res =  automate.reconnaitre_mot(mot)
        return res
    
    def tester_equivalence(self, auto1: Automate, auto2: Automate) -> bool:
        """Test d'équivalence"""
        self.operations_history.append("Test d'équivalence")
        auto1_min = self.minimiser_automate(auto1.determinisation_thompson()) if isinstance(auto1, AND) else auto1
        auto2_min = self.minimiser_automate(auto2.determinisation_thompson()) if isinstance(auto2, AND) else auto2
        return auto1_min.etats == auto2_min.etats and auto1_min.transitions == auto2_min.transitions
        
    def generer_donnees_json(self, automate: Automate) -> str:
        """JSON simplifié avec dict comprehension"""
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