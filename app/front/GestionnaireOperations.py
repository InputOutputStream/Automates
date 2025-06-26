

from itertools import product
import json
from typing import Tuple
import re

from app.front.RegexParser import RegexParser
from ..Automate import AFND, AFNS, Automate, ADC, AFDC, AND, AD, AutomateMinimal
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
        
        
    def determiniser_automate(self, automate: AND, type: int=0) -> AD:
        """Déterminise un automate"""
        self.operations_history.append("Déterminisation")
        return automate.determinisation_thompson()
        
    def minimiser_automate(self, automate: Automate) -> AFDC:
        """Minimise un automate"""
        step1 = AFDC(autre=automate)
        #result = AutomateMinimal(automate_source=step1)
        result = step1.minimiser()
        self.operations_history.append("Minimisation par fusion")
        return result

    def completer_automate(self, automate: Automate) -> ADC:
        """Complète un automate"""
        self.operations_history.append("Complétion")
        if isinstance(automate, ADC):
            return automate
        adc = AD(automate.alphabet, automate.etats, automate.etat_initial, automate.etats_finaux)
        adc.transitions = automate.transitions.copy()
        adc.completer()
        return adc
    
    def complementaire_automate(self, automate: AFDC) -> AFDC:
        """Calcule le complémentaire"""
        self.operations_history.append("Complémentation")
        at = AFDC(autre=automate)
        return at.complementaire()
    
    def automaton2eqn(self, automaton: Automate):
        """Convertit un automate en système d'équations"""
        equations = {}
        
        for etat in automaton.etats:
            equation_terms = []
            
            # Ajouter epsilon si l'état est final
            if etat in automaton.etats_finaux:
                equation_terms.append("ε")
            
            # Ajouter les transitions
            if etat in automaton.transitions:
                for symbole, destinations in automaton.transitions[etat].items():
                    for dest in destinations:
                        if symbole == "":
                            equation_terms.append(f"X{dest.nom}")
                        else:
                            equation_terms.append(f"{symbole}X{dest.nom}")
            
            equations[f"X{etat.nom}"] = " + ".join(equation_terms) if equation_terms else "∅"
        
        return equations


    def validate_equations(self, equations: dict) -> Tuple[bool, str]:
        """
        Valide un système d'équations avant l'application du lemme d'Arden.
        
        Args:
            equations (dict): Système d'équations {état: expression}
            
        Returns:
            Tuple[bool, str]: (est_valide, message_erreur)
        """
        if not equations:
            return False, "Système d'équations vide"
        
        # Vérifier que chaque état a une équation
        etats = set(equations.keys())
        
        # Extraire tous les états référencés dans les expressions
        etats_references = set()
        for etat, expression in equations.items():
            if not isinstance(expression, str):
                return False, f"Expression invalide pour l'état {etat}"
            
            # Extraire les états des termes de la forme "etat.symbole"
            termes = expression.replace(' ', '').split('+')
            for terme in termes:
                if terme and terme != 'ε':
                    if '.' in terme:
                        etat_ref = terme.split('.')[0]
                        etats_references.add(etat_ref)
                    elif terme in etats:
                        etats_references.add(terme)
        
        # Vérifier que tous les états référencés existent
        etats_manquants = etats_references - etats
        if etats_manquants:
            return False, f"États référencés mais non définis: {etats_manquants}"
        
        # Vérifier la forme des équations (détection de récursion directe)
        for etat, expression in equations.items():
            # Une équation récursive directe commence par l'état lui-même
            if expression.startswith(f"{etat}.") or expression.startswith(f"{etat}+"):
                # Valide pour le lemme d'Arden
                continue
            # Vérifier si l'état apparaît dans l'expression (récursion indirecte)
            elif f"{etat}." in expression or f"+{etat}." in expression:
                return False, f"Récursion indirecte détectée pour l'état {etat}"
        
        # Vérifier la syntaxe des expressions
        for etat, expression in equations.items():
            if not self._validate_equation_syntax(expression):
                return False, f"Syntaxe invalide dans l'équation de {etat}: {expression}"
        
        return True, "Système d'équations valide"

    def _validate_equation_syntax(self, expression: str) -> bool:
        """
        Valide la syntaxe d'une expression d'équation.
        
        Args:
            expression (str): Expression à valider
            
        Returns:
            bool: True si syntaxe valide
        """
        if not expression:
            return False
        
        # Nettoyer l'expression
        expr = expression.replace(' ', '')
        
        # Vérifier les caractères autorisés
        if not re.match(r'^[a-zA-Z0-9_.+ε|()]+$', expr):
            return False
        
        # Vérifier que l'expression ne commence/finit pas par +
        if expr.startswith('+') or expr.endswith('+'):
            return False
        
        # Vérifier les termes séparés par +
        termes = expr.split('+')
        for terme in termes:
            if not terme:  # Terme vide (++ dans l'expression)
                return False
            
            # Un terme peut être: ε, état.symbole, ou (expression)
            if terme == 'ε':
                continue
            elif '.' in terme and len(terme.split('.')) == 2:
                etat, symbole = terme.split('.')
                if not etat or not symbole:
                    return False
            elif terme.startswith('(') and terme.endswith(')'):
                # Expression parenthésée - validation récursive simplifiée
                continue
            elif re.match(r'^[a-zA-Z0-9_]+$', terme):
                # État simple
                continue
            else:
                return False
        
        return True


    def extract_variables(self, equations):
        """Extrait les variables d'un système d'équations"""
        variables = set()
        for var in equations.keys():
            variables.add(var)
        return sorted(list(variables))
    
    def automaton2reg(self, automaton: Automate):
        """Application du lemme d'arden """
        equations = self.automaton2eqn(automaton)
        variables = self.extract_variables(equations)

        return LangageReconnaissable.lemmes_arden(systeme=equations, alphabet=automaton.alphabet, variables=variables)
        
    def eqn2reg(self, equations, alphabet):
        """Application du lemme d'arden """
        variables = self.extract_variables(equations)
        return LangageReconnaissable.lemmes_arden(systeme=equations, alphabet=alphabet, variables=variables)
                

    def union_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Union de deux automates (corrigée)"""
        self.operations_history.append("Union")
        
        # Créer nouveaux états avec préfixes pour éviter les conflits
        nouveaux_etats = set()
        mapping1 = {}
        mapping2 = {}
        
        for e in auto1.etats:
            nouvel_etat = Etat(f"{e.nom}_1", est_final=e.est_final)
            nouveaux_etats.add(nouvel_etat)
            mapping1[e] = nouvel_etat
        
        for e in auto2.etats:
            nouvel_etat = Etat(f"{e.nom}_2", est_final=e.est_final)
            nouveaux_etats.add(nouvel_etat)
            mapping2[e] = nouvel_etat
        
        # Nouvel état initial
        q0 = Etat("q0_union", est_initial=True)
        nouveaux_etats.add(q0)
        
        # États finaux
        nouveaux_finaux = set()
        for e in auto1.etats_finaux:
            nouveaux_finaux.add(mapping1[e])
        for e in auto2.etats_finaux:
            nouveaux_finaux.add(mapping2[e])

        if auto1.etat_initial in auto1.etats_finaux or auto2.etat_initial in auto2.etats_finaux:
            q0.est_final = True
            nouveaux_finaux.add(q0)
      
        # Créer l'automate
        automate = AFNS(auto1.alphabet | auto2.alphabet | {""}, nouveaux_etats, q0, nouveaux_finaux)
        
        # Transitions epsilon vers les états initiaux
        automate.ajouter_transition(q0, "", mapping1[auto1.etat_initial])
        automate.ajouter_transition(q0, "", mapping2[auto2.etat_initial])
        
        # Copier transitions de auto1
        for e in auto1.etats:
            if e in auto1.transitions:
                for symbole, destinations in auto1.transitions[e].items():
                    for dest in destinations:
                        automate.ajouter_transition(mapping1[e], symbole, mapping1[dest])
        
        # Copier transitions de auto2
        for e in auto2.etats:
            if e in auto2.transitions:
                for symbole, destinations in auto2.transitions[e].items():
                    for dest in destinations:
                        automate.ajouter_transition(mapping2[e], symbole, mapping2[dest])
        
        
        return automate

            
    def intersection_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Intersection de deux automates (version corrigée)"""
        self.operations_history.append("Intersection")
        
        # L'alphabet de l'intersection est l'intersection des alphabets
        alphabet_commun = auto1.alphabet & auto2.alphabet
        
        # Si pas d'alphabet commun, retourner un automate vide
        if not alphabet_commun:
            etat_vide = Etat("vide")
            return AD(set(), {etat_vide}, etat_vide, set())
        
        # Créer seulement les états accessibles (optimisation)
        nouveaux_etats = set()
        mapping = {}
        etats_a_explorer = [(auto1.etat_initial, auto2.etat_initial)]
        etats_explores = set()
        
        # État initial
        est_final_initial = (auto1.etat_initial in auto1.etats_finaux and 
                            auto2.etat_initial in auto2.etats_finaux)
        etat_initial = Etat(f"({auto1.etat_initial.nom},{auto2.etat_initial.nom})", 
                        est_final=est_final_initial)
        nouveaux_etats.add(etat_initial)
        mapping[(auto1.etat_initial, auto2.etat_initial)] = etat_initial
        
        nouveaux_finaux = set()
        if est_final_initial:
            nouveaux_finaux.add(etat_initial)
        
        # Explorer les états accessibles
        while etats_a_explorer:
            e1, e2 = etats_a_explorer.pop(0)
            
            if (e1, e2) in etats_explores:
                continue
            etats_explores.add((e1, e2))
            
            etat_source = mapping[(e1, e2)]
            
            # Pour chaque symbole de l'alphabet commun
            for symbole in alphabet_commun:
                # Vérifier les transitions depuis e1 et e2
                dest1_set = set()
                if e1 in auto1.transitions and symbole in auto1.transitions[e1]:
                    dest1_set = auto1.transitions[e1][symbole]
                
                dest2_set = set()
                if e2 in auto2.transitions and symbole in auto2.transitions[e2]:
                    dest2_set = auto2.transitions[e2][symbole]
                
                # Produit cartésien des destinations
                for dest1 in dest1_set:
                    for dest2 in dest2_set:
                        # Créer l'état destination s'il n'existe pas
                        if (dest1, dest2) not in mapping:
                            est_final = (dest1 in auto1.etats_finaux and 
                                    dest2 in auto2.etats_finaux)
                            nouvel_etat = Etat(f"({dest1.nom},{dest2.nom})", 
                                            est_final=est_final)
                            nouveaux_etats.add(nouvel_etat)
                            mapping[(dest1, dest2)] = nouvel_etat
                            
                            if est_final:
                                nouveaux_finaux.add(nouvel_etat)
                            
                            # Ajouter à la file d'exploration
                            etats_a_explorer.append((dest1, dest2))
                        
                        etat_dest = mapping[(dest1, dest2)]
                        
                        # Créer l'automate s'il n'existe pas encore
                        if 'automate' not in locals():
                            automate = AD(alphabet_commun, nouveaux_etats, etat_initial, nouveaux_finaux)
                        
                        # Ajouter la transition
                        automate.ajouter_transition(etat_source, symbole, etat_dest)
        
        # Si aucune transition n'a été créée, créer l'automate maintenant
        if 'automate' not in locals():
            automate = AD(alphabet_commun, nouveaux_etats, etat_initial, nouveaux_finaux)
        
        return automate


    # Version alternative plus propre
    def intersection_automates_v2(self, auto1: Automate, auto2: Automate) -> Automate:
        """Intersection de deux automates - version alternative plus claire"""
        self.operations_history.append("Intersection")
        
        # L'alphabet de l'intersection est l'intersection des alphabets
        alphabet_commun = auto1.alphabet & auto2.alphabet
        
        # Initialisation
        nouveaux_etats = set()
        nouveaux_finaux = set()
        mapping = {}
        
        # État initial
        paire_initiale = (auto1.etat_initial, auto2.etat_initial)
        est_final_initial = (auto1.etat_initial in auto1.etats_finaux and 
                            auto2.etat_initial in auto2.etats_finaux)
        
        etat_initial = Etat(f"({auto1.etat_initial.nom},{auto2.etat_initial.nom})", 
                        est_final=est_final_initial)
        nouveaux_etats.add(etat_initial)
        mapping[paire_initiale] = etat_initial
        
        if est_final_initial:
            nouveaux_finaux.add(etat_initial)
        
        # Créer l'automate
        automate = AD(alphabet_commun, nouveaux_etats, etat_initial, nouveaux_finaux)
        
        # File d'exploration (BFS)
        file_exploration = [paire_initiale]
        explores = set()
        
        while file_exploration:
            e1, e2 = file_exploration.pop(0)
            
            if (e1, e2) in explores:
                continue
            explores.add((e1, e2))
            
            etat_source = mapping[(e1, e2)]
            
            # Explorer les transitions pour chaque symbole commun
            for symbole in alphabet_commun:
                # Obtenir les destinations possibles
                dest1_list = []
                if e1 in auto1.transitions and symbole in auto1.transitions[e1]:
                    dest1_list = list(auto1.transitions[e1][symbole])
                
                dest2_list = []
                if e2 in auto2.transitions and symbole in auto2.transitions[e2]:
                    dest2_list = list(auto2.transitions[e2][symbole])
                
                # Créer les transitions du produit cartésien
                for dest1 in dest1_list:
                    for dest2 in dest2_list:
                        paire_dest = (dest1, dest2)
                        
                        # Créer l'état destination s'il n'existe pas
                        if paire_dest not in mapping:
                            est_final = (dest1 in auto1.etats_finaux and 
                                    dest2 in auto2.etats_finaux)
                            
                            etat_dest = Etat(f"({dest1.nom},{dest2.nom})", 
                                        est_final=est_final)
                            
                            nouveaux_etats.add(etat_dest)
                            automate.etats.add(etat_dest)
                            mapping[paire_dest] = etat_dest
                            
                            if est_final:
                                nouveaux_finaux.add(etat_dest)
                                automate.etats_finaux.add(etat_dest)
                            
                            # Ajouter à la file d'exploration
                            file_exploration.append(paire_dest)
                        
                        etat_dest = mapping[paire_dest]
                        automate.ajouter_transition(etat_source, symbole, etat_dest)
        
        return automate
            
    def concatenation_automates(self, auto1: Automate, auto2: Automate) -> Automate:
        """Concaténation de deux automates (corrigée)"""
        self.operations_history.append("Concaténation")
        
        # Créer nouveaux états avec préfixes
        nouveaux_etats = set()
        mapping1 = {}
        mapping2 = {}
        
        for e in auto1.etats:
            nouvel_etat = Etat(f"{e.nom}_1", est_final=False)  # Pas final pour auto1
            nouveaux_etats.add(nouvel_etat)
            mapping1[e] = nouvel_etat
        
        for e in auto2.etats:
            nouvel_etat = Etat(f"{e.nom}_2", est_final=e.est_final)
            nouveaux_etats.add(nouvel_etat)
            mapping2[e] = nouvel_etat
        
        # État initial et finaux
        etat_initial = mapping1[auto1.etat_initial]
        nouveaux_finaux = {mapping2[e] for e in auto2.etats_finaux}
        
        # Créer l'automate
        automate = AFNS(auto1.alphabet | auto2.alphabet | {""}, nouveaux_etats, etat_initial, nouveaux_finaux)
        
        # Copier transitions de auto1
        for e in auto1.etats:
            if e in auto1.transitions:
                for symbole, destinations in auto1.transitions[e].items():
                    for dest in destinations:
                        automate.ajouter_transition(mapping1[e], symbole, mapping1[dest])
        
        # Copier transitions de auto2
        for e in auto2.etats:
            if e in auto2.transitions:
                for symbole, destinations in auto2.transitions[e].items():
                    for dest in destinations:
                        automate.ajouter_transition(mapping2[e], symbole, mapping2[dest])
        
        # Transitions epsilon des états finaux de auto1 vers l'état initial de auto2
        for e_final in auto1.etats_finaux:
            automate.ajouter_transition(mapping1[e_final], "", mapping2[auto2.etat_initial])
        
        return automate   
        
    def etoile_automate(self, automate: Automate) -> Automate:
        """Étoile de Kleene d'un automate (corrigée)"""
        self.operations_history.append("Étoile de Kleene")
        
        # Créer nouveaux états
        nouveaux_etats = set()
        mapping = {}
        
        for e in automate.etats:
            nouvel_etat = Etat(f"{e.nom}_star", est_final=e.est_final)
            nouveaux_etats.add(nouvel_etat)
            mapping[e] = nouvel_etat
        
        
        # Nouvel état initial qui est aussi final (pour ε)
        q0 = Etat("q0_star", est_initial=True, est_final=True)
        nouveaux_etats.add(q0)
        
        # États finaux: le nouvel état initial + les anciens états finaux
        nouveaux_finaux = {q0} | {mapping[e] for e in automate.etats_finaux}

        if automate.etat_initial in automate.etats_finaux:
            q0.est_final = True
            nouveaux_finaux.add(q0)
        
        # Créer l'automate
        automate_resultat = AFNS(automate.alphabet | {""}, nouveaux_etats, q0, nouveaux_finaux)
        
        # Transition epsilon vers l'ancien état initial
        automate_resultat.ajouter_transition(q0, "", mapping[automate.etat_initial])
        
        # Copier toutes les transitions
        for e in automate.etats:
            if e in automate.transitions:
                for symbole, destinations in automate.transitions[e].items():
                    for dest in destinations:
                        automate_resultat.ajouter_transition(mapping[e], symbole, mapping[dest])
        
        # Transitions epsilon des états finaux vers l'état initial (pour répétition)
        for e_final in automate.etats_finaux:
            automate_resultat.ajouter_transition(mapping[e_final], "", mapping[automate.etat_initial])
        
        return automate_resultat
        
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
