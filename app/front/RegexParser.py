
from typing import Tuple
import uuid
from ..Automate import AFNS
from ..Etat import Etat

class RegexParser:
    """
    Parseur d'expressions régulières utilisant l'algorithme de Thompson
    """
    
    def __init__(self):
        """Initialise le parseur"""
        self.position = 0
        self.expression = ""
        
    def parser_regex(self, expression: str) -> 'AFNS':
        """Parse une regex et retourne l'automate équivalent"""
        self.expression = expression
        self.position = 0
        
        # Validation de la syntaxe
        est_valide, message = self.valider_syntaxe(expression)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        # Parsing et construction de l'automate
        automate = self._parser_expression()
        return automate
    
    def valider_syntaxe(self, expression: str) -> Tuple[bool, str]:
        """Valide la syntaxe d'une regex"""
        if not expression:
            return False, "Expression vide"
        
        # Vérification des parenthèses équilibrées
        compteur_parentheses = 0
        for i, char in enumerate(expression):
            if char == '(':
                compteur_parentheses += 1
            elif char == ')':
                compteur_parentheses -= 1
                if compteur_parentheses < 0:
                    return False, f"Parenthèse fermante non appariée à la position {i}"
        
        if compteur_parentheses != 0:
            return False, "Parenthèses non équilibrées"
        
        # Vérification des opérateurs mal placés
        for i, char in enumerate(expression):
            if char in '*+?':
                if i == 0:
                    return False, f"Opérateur {char} en début d'expression"
                if expression[i-1] in '|(':
                    return False, f"Opérateur {char} mal placé à la position {i}"
        
        return True, "Syntaxe valide"
    
    def _parser_expression(self) -> 'AFNS':
        """Parse une expression (gère l'union |)"""
        gauche = self._parser_terme()
        
        while self.position < len(self.expression) and self.expression[self.position] == '|':
            self.position += 1  # Passer le '|'
            droite = self._parser_terme()
            gauche = self.construire_union(gauche, droite)
        
        return gauche
    
    def _parser_terme(self) -> 'AFNS':
        """Parse un terme (gère la concaténation)"""
        gauche = self._parser_facteur()
        
        while (self.position < len(self.expression) and 
               self.expression[self.position] not in '|)'):
            droite = self._parser_facteur()
            gauche = self.construire_concatenation(gauche, droite)
        
        return gauche
    
    def _parser_facteur(self) -> 'AFNS':
        """Parse un facteur (gère *, +, ?)"""
        base = self._parser_base()
        
        while self.position < len(self.expression):
            char = self.expression[self.position]
            if char == '*':
                base = self.construire_etoile(base)
                self.position += 1
            elif char == '+':
                base = self.construire_plus(base)
                self.position += 1
            elif char == '?':
                base = self.construire_optionnel(base)
                self.position += 1
            else:
                break
        
        return base
    
    def _parser_base(self) -> 'AFNS':
        """Parse un élément de base (symbole ou expression parenthésée)"""
        if self.position >= len(self.expression):
            raise ValueError("Expression incomplète")
        
        char = self.expression[self.position]
        
        if char == '(':
            self.position += 1  # Passer '('
            expr = self._parser_expression()
            if self.position >= len(self.expression) or self.expression[self.position] != ')':
                raise ValueError("Parenthèse fermante manquante")
            self.position += 1  # Passer ')'
            return expr
        else:
            self.position += 1
            return self.construire_automate_base(char)
    
    def construire_automate_base(self, symbole: str) -> 'AFNS':
        """Construit l'automate de base pour un symbole"""        
        q0 = Etat(f"q{uuid.uuid4().hex[:8]}")
        q1 = Etat(f"q{uuid.uuid4().hex[:8]}", est_final=True)
        
        automate = AFNS(
            alphabet={symbole},
            etats={q0, q1},
            etat_initial=q0,
            etats_finaux={q1}
        )
        
        automate.ajouter_transition(q0, symbole, q1)
        return automate
    
    def construire_union(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        """Construit l'union de deux automates (a|b)"""
                
        # Nouvel état initial et final
        nouvel_initial = Etat(f"q{uuid.uuid4().hex[:8]}")
        nouvel_final = Etat(f"q{uuid.uuid4().hex[:8]}", est_final=True)
        
        # Union des alphabets et états
        nouvel_alphabet = auto1.alphabet | auto2.alphabet
        nouveaux_etats = {nouvel_initial, nouvel_final} | auto1.etats | auto2.etats
        
        # Marquer les anciens états finaux comme non-finaux
        for etat in auto1.etats_finaux | auto2.etats_finaux:
            etat.est_final = False
        
        # Créer le nouvel automate
        automate = AFNS(
            alphabet=nouvel_alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )
        
        # Copier les transitions des automates originaux
        for source in auto1.transitions:
            for symbole in auto1.transitions[source]:
                for dest in auto1.transitions[source][symbole]:
                    automate.ajouter_transition(source, symbole, dest)
        
        for source in auto2.transitions:
            for symbole in auto2.transitions[source]:
                for dest in auto2.transitions[source][symbole]:
                    automate.ajouter_transition(source, symbole, dest)
        
        # Ajouter les ε-transitions
        automate.ajouter_transition_epsilon(nouvel_initial, auto1.etat_initial)
        automate.ajouter_transition_epsilon(nouvel_initial, auto2.etat_initial)
        
        for etat_final in auto1.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, nouvel_final)
        for etat_final in auto2.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        return automate
    
    def construire_concatenation(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        """Construit la concaténation (ab)"""
        # Union des alphabets et états
        nouvel_alphabet = auto1.alphabet | auto2.alphabet
        nouveaux_etats = auto1.etats | auto2.etats
        
        # L'état initial du premier automate devient l'état initial
        # Les états finaux du second automate deviennent les états finaux
        
        # Marquer les anciens états finaux du premier automate comme non-finaux
        for etat in auto1.etats_finaux:
            etat.est_final = False
        
        # Créer le nouvel automate
        automate = AFNS(
            alphabet=nouvel_alphabet,
            etats=nouveaux_etats,
            etat_initial=auto1.etat_initial,
            etats_finaux=auto2.etats_finaux
        )
        
        # Copier toutes les transitions
        for source in auto1.transitions:
            for symbole in auto1.transitions[source]:
                for dest in auto1.transitions[source][symbole]:
                    automate.ajouter_transition(source, symbole, dest)
        
        for source in auto2.transitions:
            for symbole in auto2.transitions[source]:
                for dest in auto2.transitions[source][symbole]:
                    automate.ajouter_transition(source, symbole, dest)
        
        # Ajouter les ε-transitions des états finaux de auto1 vers l'état initial de auto2
        for etat_final in auto1.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, auto2.etat_initial)
        
        return automate
    
    def construire_etoile(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'étoile de Kleene (a*)"""
                
        nouvel_initial = Etat(f"q{uuid.uuid4().hex[:8]}", est_final=True)
        nouveaux_etats = {nouvel_initial} | automate.etats
        
        # Créer le nouvel automate
        nouvel_automate = AFNS(
            alphabet=automate.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_initial} | automate.etats_finaux
        )
        
        # Copier les transitions
        for source in automate.transitions:
            for symbole in automate.transitions[source]:
                for dest in automate.transitions[source][symbole]:
                    nouvel_automate.ajouter_transition(source, symbole, dest)
        
        # Ajouter les ε-transitions
        nouvel_automate.ajouter_transition_epsilon(nouvel_initial, automate.etat_initial)
        
        for etat_final in automate.etats_finaux:
            nouvel_automate.ajouter_transition_epsilon(etat_final, automate.etat_initial)
        
        return nouvel_automate
    
    def construire_plus(self, automate: 'AFNS') -> 'AFNS':
        """Construit A+ équivalent à AA*"""
        etoile = self.construire_etoile(automate)
        return self.construire_concatenation(automate, etoile)
    
    def construire_optionnel(self, automate: 'AFNS') -> 'AFNS':
        """Construit A? équivalent à (A|ε)"""
                
        nouvel_initial = Etat(f"q{uuid.uuid4().hex[:8]}", est_final=True)
        nouveaux_etats = {nouvel_initial} | automate.etats
        
        # Créer le nouvel automate
        nouvel_automate = AFNS(
            alphabet=automate.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_initial} | automate.etats_finaux
        )
        
        # Copier les transitions
        for source in automate.transitions:
            for symbole in automate.transitions[source]:
                for dest in automate.transitions[source][symbole]:
                    nouvel_automate.ajouter_transition(source, symbole, dest)
        
        # Ajouter l'ε-transition
        nouvel_automate.ajouter_transition_epsilon(nouvel_initial, automate.etat_initial)
        
        return nouvel_automate


