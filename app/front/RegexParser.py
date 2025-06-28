from typing import Tuple, Set, List
import copy
from ..Automate import Automate, AFNS, AD
from ..Etat import Etat
from ..RegexNode import *
from ..LangageReconnaissable import LangageReconnaissable

class RegexParser:
    """
    Parseur d'expressions régulières utilisant l'algorithme de Thompson
    """
    
    def __init__(self):
        """Initialise le parseur"""
        self.position = 0
        self.expression = ""
        self.compteur_etats = 0
        
    def _generer_nom_etat(self, prefix: str = "q") -> str:
        """Génère un nom d'état unique"""
        nom = f"{prefix}{self.compteur_etats}"
        self.compteur_etats += 1
        return nom
    
    def _reinitialiser_compteur(self):
        """Remet le compteur d'états à zéro"""
        self.compteur_etats = 0
        
    def parser_regex(self, expression: str) -> 'AFNS':
        """Parse une regex et retourne l'automate équivalent"""
        expression = LangageReconnaissable.simplify_regex(expression)
        self.expression = expression
        self.position = 0
        self.compteur_etats = 0
        
        est_valide, message = RegexParser.valider_syntaxe(expression)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        return self._parser_expression()
    
    @classmethod
    def _compute_ast_properties(cls, node: RegexNode) -> ASTProperties:
        """Calcule les propriétés de l'AST pour la construction de Glushkov"""
        props = ASTProperties()
        position_counter = [1]  # Compteur mutable pour les positions
        
        def traverse(node: RegexNode) -> ASTProperties:
            local_props = ASTProperties()
            
            if isinstance(node, SymbolNode):
                # Attribuer une nouvelle position
                pos = position_counter[0]
                position_counter[0] += 1
                
                local_props.positions = {pos: node.symbol}
                local_props.first = {pos}
                local_props.last = {pos}
                local_props.nullable = False
                return local_props
                
            elif isinstance(node, UnionNode):
                left_props = traverse(node.left)
                right_props = traverse(node.right)
                
                local_props.positions = {**left_props.positions, **right_props.positions}
                local_props.first = left_props.first | right_props.first
                local_props.last = left_props.last | right_props.last
                local_props.nullable = left_props.nullable or right_props.nullable
                
                # Fusionner les relations follow
                for k, v in left_props.follow.items():
                    local_props.follow[k] = v.copy()
                for k, v in right_props.follow.items():
                    local_props.follow[k].update(v)
                    
                return local_props
                
            elif isinstance(node, ConcatNode):
                left_props = traverse(node.left)
                right_props = traverse(node.right)
                
                local_props.positions = {**left_props.positions, **right_props.positions}
                local_props.nullable = left_props.nullable and right_props.nullable
                
                # Calculer first
                local_props.first = left_props.first
                if left_props.nullable:
                    local_props.first |= right_props.first
                    
                # Calculer last
                local_props.last = right_props.last
                if right_props.nullable:
                    local_props.last |= left_props.last
                    
                # Fusionner follow + ajouter les connections
                for k, v in left_props.follow.items():
                    local_props.follow[k] = v.copy()
                for k, v in right_props.follow.items():
                    local_props.follow[k].update(v)
                    
                # Concaténation: les derniers de gauche suivent les premiers de droite
                for left_last in left_props.last:
                    local_props.follow[left_last].update(right_props.first)
                    
                return local_props
                
            elif isinstance(node, StarNode):
                child_props = traverse(node.child)
                
                local_props.positions = child_props.positions
                local_props.first = child_props.first
                local_props.last = child_props.last
                local_props.nullable = True  # L'étoile inclut le vide
                
                # Copier les relations follow
                for k, v in child_props.follow.items():
                    local_props.follow[k] = v.copy()
                    
                # Ajouter les boucles: les derniers suivent les premiers
                for last_pos in child_props.last:
                    local_props.follow[last_pos].update(child_props.first)
                    
                return local_props
                
            elif isinstance(node, PlusNode):
                child_props = traverse(node.child)
                
                local_props.positions = child_props.positions
                local_props.first = child_props.first
                local_props.last = child_props.last
                local_props.nullable = child_props.nullable  # Même nullable que l'enfant
                
                # Copier les relations follow
                for k, v in child_props.follow.items():
                    local_props.follow[k] = v.copy()
                    
                # Ajouter les boucles: les derniers suivent les premiers
                for last_pos in child_props.last:
                    local_props.follow[last_pos].update(child_props.first)
                    
                return local_props
                
            elif isinstance(node, OptionalNode):
                child_props = traverse(node.child)
                
                local_props.positions = child_props.positions
                local_props.first = child_props.first
                local_props.last = child_props.last
                local_props.nullable = True  # L'optionnel inclut le vide
                
                # Copier les relations follow
                for k, v in child_props.follow.items():
                    local_props.follow[k] = v.copy()
                    
                return local_props
                
            else:
                raise ValueError(f"Type de nœud non supporté: {type(node)}")
        
        return traverse(node)

    @classmethod
    def construire_automate_glushkov(cls, regex: str) -> 'AD':
        """Construction de Glushkov optimisée"""
        parser = cls()
        parser.expression = regex
        parser.position = 0
        parser.compteur_etats = 0
        
        est_valide, message = cls.valider_syntaxe(regex)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        ast = parser._construire_ast()
        props = cls._compute_ast_properties(ast)
        
        etat_initial = Etat("q0")
        etats = {etat_initial}
        pos_to_etat = {pos: Etat(f"q{pos}") for pos, symbole in props.positions.items() if symbole != '#'}
        etats.update(pos_to_etat.values())
        
        alphabet = {sym for sym in props.positions.values() if sym != '#'}
        transitions = {}
        
        # Transitions depuis l'état initial
        for symbole in alphabet:
            destinations = {pos_to_etat[pos] for pos in props.first 
                        if props.positions.get(pos) == symbole and pos in pos_to_etat}
            if destinations:
                transitions.setdefault(etat_initial, {})[symbole] = destinations
        
        # Transitions entre positions
        for pos, symbole in props.positions.items():
            if symbole != '#' and pos in pos_to_etat:
                etat_source = pos_to_etat[pos]
                for follow_pos in props.follow.get(pos, set()):
                    follow_symbole = props.positions.get(follow_pos)
                    if follow_symbole and follow_symbole != '#' and follow_pos in pos_to_etat:
                        transitions.setdefault(etat_source, {}).setdefault(
                            follow_symbole, set()).add(pos_to_etat[follow_pos])
        
        # États finaux
        etats_finaux = set()
        if props.nullable:
            etats_finaux.add(etat_initial)
        etats_finaux.update(pos_to_etat[pos] for pos in props.last if pos in pos_to_etat)
        
        automate = AD(
            alphabet=alphabet,
            etats=etats,
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        automate.transitions = transitions
        return automate


    @classmethod
    def construire_automate_thompson(cls, expression: str) -> 'AFNS':
        """Construction de Thompson optimisée"""
        parser = cls()
        parser.expression = expression
        parser.position = 0
        parser.compteur_etats = 0
        parser._transitions = {}
        
        ast = parser._parser_expression_ast()
        initial, final = parser._build_thompson(ast)
        
        etats = parser._collect_states(initial)
        alphabet = parser._collect_alphabet(ast)
        
        automate = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=initial,
            etats_finaux={final}
        )
        automate.transitions = parser._transitions
        return automate

    def _construire_ast(self) -> RegexNode:
        """Construit l'AST de la regex"""
        return self._parser_expression_ast()

    def _parser_expression_ast(self) -> RegexNode:
        """Parse une expression et retourne l'AST (gère l'union |)"""
        gauche = self._parser_terme_ast()
        
        while self.position < len(self.expression) and self.expression[self.position] == '|':
            self.position += 1
            droite = self._parser_terme_ast()
            gauche = UnionNode(gauche, droite)
        
        return gauche

    def _parser_terme_ast(self) -> RegexNode:
        """Parse un terme et retourne l'AST (gère la concaténation)"""
        gauche = self._parser_facteur_ast()
        
        while (self.position < len(self.expression) and 
               self.expression[self.position] not in '|)'):
            droite = self._parser_facteur_ast()
            gauche = ConcatNode(gauche, droite)
        
        return gauche

    def _parser_facteur_ast(self) -> RegexNode:
        """Parse un facteur et retourne l'AST (gère *, +, ?)"""
        base = self._parser_base_ast()
        
        while self.position < len(self.expression):
            char = self.expression[self.position]
            if char == '*':
                base = StarNode(base)
                self.position += 1
            elif char == '+':
                base = PlusNode(base)
                self.position += 1
            elif char == '?':
                base = OptionalNode(base)
                self.position += 1
            else:
                break
        
        return base

    def _parser_base_ast(self) -> RegexNode:
        """Parse un élément de base et retourne l'AST"""
        if self.position >= len(self.expression):
            raise ValueError("Expression incomplète")
        
        char = self.expression[self.position]
        
        if char == '(':
            self.position += 1
            expr = self._parser_expression_ast()
            if self.position >= len(self.expression) or self.expression[self.position] != ')':
                raise ValueError("Parenthèse fermante manquante")
            self.position += 1
            return expr
        else:
            self.position += 1
            return SymbolNode(char)

    @classmethod
    def construire_automate_thompson(cls, expression: str) -> 'AFNS':
        """Construction de Thompson optimisée"""
        parser = cls()
        parser.expression = expression
        parser.position = 0
        parser._reinitialiser_compteur()
        
        ast = parser._parser_expression_ast()
        initial, final = parser._build_thompson(ast)
        
        # Collecter tous les états
        etats = parser._collect_states(initial)
        alphabet = parser._collect_alphabet(ast)
        
        automate = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=initial,
            etats_finaux={final}
        )
        automate.transitions = getattr(parser, '_transitions', {})
        
        return automate

    def _build_thompson(self, node: RegexNode) -> Tuple[Etat, Etat]:
        """Construction récursive de Thompson retournant (début, fin)"""
        if not hasattr(self, '_transitions'):
            self._transitions = {}
            
        if isinstance(node, SymbolNode):
            start = Etat(self._generer_nom_etat())
            end = Etat(self._generer_nom_etat(), est_final=True)
            self._add_transition(start, node.symbol, end)
            return start, end
            
        elif isinstance(node, UnionNode):
            start = Etat(self._generer_nom_etat())
            end = Etat(self._generer_nom_etat(), est_final=True)
            
            left_start, left_end = self._build_thompson(node.left)
            right_start, right_end = self._build_thompson(node.right)
            
            self._add_epsilon(start, left_start)
            self._add_epsilon(start, right_start)
            self._add_epsilon(left_end, end)
            self._add_epsilon(right_end, end)
            
            left_end.est_final = False
            right_end.est_final = False
            
            return start, end
            
        elif isinstance(node, ConcatNode):
            left_start, left_end = self._build_thompson(node.left)
            right_start, right_end = self._build_thompson(node.right)
            
            self._add_epsilon(left_end, right_start)
            left_end.est_final = False
            
            return left_start, right_end
            
        elif isinstance(node, StarNode):
            start = Etat(self._generer_nom_etat())
            end = Etat(self._generer_nom_etat(), est_final=True)
            
            sub_start, sub_end = self._build_thompson(node.child)
            
            self._add_epsilon(start, end)  # ε path
            self._add_epsilon(start, sub_start)
            self._add_epsilon(sub_end, end)
            self._add_epsilon(sub_end, sub_start)  # Loop back
            
            sub_end.est_final = False
            
            return start, end
            
        elif isinstance(node, PlusNode):
            # A+ = AA* - version simplifiée
            child_start, child_end = self._build_thompson(node.child)
            
            # Créer le nœud étoile et l'attacher
            star_start = Etat(self._generer_nom_etat())
            star_end = Etat(self._generer_nom_etat(), est_final=True)
            
            # Connections pour A*
            self._add_epsilon(star_start, star_end)  # ε path
            self._add_epsilon(star_start, child_start)
            self._add_epsilon(child_end, star_end)
            self._add_epsilon(child_end, child_start)  # Loop back
            
            # Connection A avec A*
            self._add_epsilon(child_end, star_start)
            child_end.est_final = False
            
            return child_start, star_end


        elif isinstance(node, OptionalNode):
            start = Etat(self._generer_nom_etat())
            end = Etat(self._generer_nom_etat(), est_final=True)
            
            sub_start, sub_end = self._build_thompson(node.child)
            
            self._add_epsilon(start, end)  # Skip path
            self._add_epsilon(start, sub_start)
            self._add_epsilon(sub_end, end)
            
            sub_end.est_final = False
            
            return start, end
        
        else:
            raise ValueError(f"Type de nœud non supporté: {type(node)}")

    def _add_transition(self, source: Etat, symbol: str, dest: Etat):
        """Ajoute une transition"""
        self._transitions.setdefault(source, {}).setdefault(symbol, set()).add(dest)

    def _add_epsilon(self, source: Etat, dest: Etat):
        """Ajoute une transition epsilon"""
        self._add_transition(source, '', dest)

    def _collect_states(self, start: Etat) -> Set[Etat]:
        """Collecte tous les états par parcours BFS"""
        visited = set()
        queue = [start]
        
        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)
            
            if hasattr(self, '_transitions') and state in self._transitions:
                for transitions in self._transitions[state].values():
                    queue.extend(transitions)
        
        return visited

    def _collect_alphabet(self, node: RegexNode) -> Set[str]:
        """Collecte l'alphabet depuis l'AST"""
        if isinstance(node, SymbolNode):
            return {node.symbol}
        elif isinstance(node, (UnionNode, ConcatNode)):
            return self._collect_alphabet(node.left) | self._collect_alphabet(node.right)
        elif isinstance(node, (StarNode, PlusNode, OptionalNode)):
            return self._collect_alphabet(node.child)
        return set()

    @classmethod
    def valider_syntaxe(cls, expression: str) -> Tuple[bool, str]:
        """Valide la syntaxe d'une regex"""
        if not expression:
            return False, "Expression vide"
        
        # Vérification des parenthèses
        compteur = 0
        for i, char in enumerate(expression):
            if char == '(':
                compteur += 1
            elif char == ')':
                compteur -= 1
                if compteur < 0:
                    return False, f"Parenthèse fermante non appariée à la position {i}"
        
        if compteur != 0:
            return False, "Parenthèses non équilibrées"
        
        # Vérification des opérateurs
        for i, char in enumerate(expression):
            if char in '*+?':
                if i == 0 or expression[i-1] in '|(':
                    return False, f"Opérateur {char} mal placé à la position {i}"
            elif char == '|':
                if i == 0 or i == len(expression) - 1:
                    return False, f"Alternation vide à la position {i}"
                if expression[i-1] in '|(' or expression[i+1] in '|)':
                    return False, f"Alternation vide à la position {i}"
        
        # Vérification des doubles opérateurs
        for i in range(len(expression) - 1):
            if expression[i] in '*+?' and expression[i+1] in '*+?':
                return False, f"Opérateurs consécutifs à la position {i}"
            if expression[i] == '|' and expression[i+1] == '|':
                return False, f"Alternations consécutives à la position {i}"
        
        return True, "Syntaxe valide"
    
    # Méthodes pour la construction classique (inchangées car déjà optimales)
    
    def _parser_expression(self) -> 'AFNS':
        """Parse une expression (gère l'union |)"""
        gauche = self._parser_terme()
        
        while self.position < len(self.expression) and self.expression[self.position] == '|':
            self.position += 1
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
            self.position += 1
            expr = self._parser_expression()
            if self.position >= len(self.expression) or self.expression[self.position] != ')':
                raise ValueError("Parenthèse fermante manquante")
            self.position += 1
            return expr
        else:
            self.position += 1
            return self.construire_automate_base(char)

    def construire_automate_base(self, symbole: str) -> 'AFNS':
        """Construit l'automate de base pour un symbole"""        
        q0 = Etat(self._generer_nom_etat())
        q1 = Etat(self._generer_nom_etat(), est_final=True)
        
        automate = AFNS(
            alphabet={symbole},
            etats={q0, q1},
            etat_initial=q0,
            etats_finaux={q1}
        )
        
        automate.ajouter_transition(q0, symbole, q1)
        return automate
        
    def _copier_automate(self, automate: Automate):
        return copy.deepcopy(automate)
    
    def construire_concatenation(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        auto1_copy = self._copier_automate(auto1)
        auto2_copy = self._copier_automate(auto2)

        # Fusion des alphabets et états
        alphabet = auto1_copy.alphabet | auto2_copy.alphabet
        etats = set()
        etats.update(auto1_copy.etats)
        etats.update(auto2_copy.etats)

        # Les anciens états finaux de auto1 ne sont plus finaux
        for etat in auto1_copy.etats_finaux:
            etat.est_final = False

        # Construction de l'automate
        automate = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=auto1_copy.etat_initial,
            etats_finaux=auto2_copy.etats_finaux
        )

        # Copier les transitions
        for source, trans in list(auto1_copy.transitions.items()) + list(auto2_copy.transitions.items()):
            for symbole, destinations in trans.items():
                for dest in destinations:
                    automate.ajouter_transition(source, symbole, dest)

        # Ajouter les ε-transitions des états finaux de auto1 vers l'état initial de auto2
        for etat_final in auto1_copy.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, auto2_copy.etat_initial)

        return automate
    
    def construire_union(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        auto1_copy = self._copier_automate(auto1)
        auto2_copy = self._copier_automate(auto2)

        nouvel_initial = Etat(self._generer_nom_etat())
        nouvel_final = Etat(self._generer_nom_etat(), est_final=True)

        # Fusion des alphabets et états
        alphabet = auto1_copy.alphabet | auto2_copy.alphabet
        etats = set()
        etats.add(nouvel_initial)
        etats.add(nouvel_final)
        etats.update(auto1_copy.etats)
        etats.update(auto2_copy.etats)

        # Les anciens états finaux ne sont plus finaux
        for etat in auto1_copy.etats_finaux | auto2_copy.etats_finaux:
            etat.est_final = False

        # Construction de l'automate
        automate = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )

        # Copier les transitions
        for source, trans in list(auto1_copy.transitions.items()) + list(auto2_copy.transitions.items()):
            for symbole, destinations in trans.items():
                for dest in destinations:
                    automate.ajouter_transition(source, symbole, dest)

        # Ajouter les ε-transitions
        automate.ajouter_transition_epsilon(nouvel_initial, auto1_copy.etat_initial)
        automate.ajouter_transition_epsilon(nouvel_initial, auto2_copy.etat_initial)

        for etat_final in auto1_copy.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, nouvel_final)
        for etat_final in auto2_copy.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, nouvel_final)

        return automate
    
    def construire_etoile(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'automate pour l'opération étoile (*)"""
        auto_copy = self._copier_automate(automate)
        
        nouvel_initial = Etat(self._generer_nom_etat())
        nouvel_final = Etat(self._generer_nom_etat(), est_final=True)
        
        # Fusion des alphabets et états
        alphabet = auto_copy.alphabet
        etats = set()
        etats.add(nouvel_initial)
        etats.add(nouvel_final)
        etats.update(auto_copy.etats)
        
        # Les anciens états finaux ne sont plus finaux
        for etat in auto_copy.etats_finaux:
            etat.est_final = False
        
        # Construction de l'automate
        automate_etoile = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )
        
        # Copier les transitions
        for source, trans in auto_copy.transitions.items():
            for symbole, destinations in trans.items():
                for dest in destinations:
                    automate_etoile.ajouter_transition(source, symbole, dest)
        
        # Ajouter les ε-transitions pour l'étoile
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        for etat_final in auto_copy.etats_finaux:
            automate_etoile.ajouter_transition_epsilon(etat_final, nouvel_final)
            automate_etoile.ajouter_transition_epsilon(etat_final, auto_copy.etat_initial)
        
        return automate_etoile
    
    def construire_plus(self, automate: 'AFNS') -> 'AFNS':
        """Construction directe pour A+"""
        auto_copy = self._copier_automate(automate)
        
        # Ajouter transitions de retour depuis les états finaux vers l'initial
        for etat_final in list(auto_copy.etats_finaux):
            auto_copy.ajouter_transition_epsilon(etat_final, auto_copy.etat_initial)
        
        return auto_copy
    
    def construire_optionnel(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'automate pour l'opération optionnelle (?)"""
        auto_copy = self._copier_automate(automate)
        
        nouvel_initial = Etat(self._generer_nom_etat())
        nouvel_final = Etat(self._generer_nom_etat(), est_final=True)
        
        # Fusion des alphabets et états
        alphabet = auto_copy.alphabet
        etats = set()
        etats.add(nouvel_initial)
        etats.add(nouvel_final)
        etats.update(auto_copy.etats)
        
        # Les anciens états finaux ne sont plus finaux
        for etat in auto_copy.etats_finaux:
            etat.est_final = False
        
        # Construction de l'automate
        automate_opt = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )
        
        # Copier les transitions
        for source, trans in auto_copy.transitions.items():
            for symbole, destinations in trans.items():
                for dest in destinations:
                    automate_opt.ajouter_transition(source, symbole, dest)
        
        # Ajouter les ε-transitions pour l'optionnel
        automate_opt.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        automate_opt.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        for etat_final in auto_copy.etats_finaux:
            automate_opt.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        return automate_opt

    def construire_intersection(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        """Construction d'intersection par produit cartésien"""
        ad1 = auto1.determiniser() if hasattr(auto1, 'determiniser') else auto1
        ad2 = auto2.determiniser() if hasattr(auto2, 'determiniser') else auto2
        
        alphabet = ad1.alphabet & ad2.alphabet
        etat_initial = Etat(f"({ad1.etat_initial.nom},{ad2.etat_initial.nom})")
        etat_initial.est_final = (ad1.etat_initial in ad1.etats_finaux and 
                                ad2.etat_initial in ad2.etats_finaux)
        
        automate_inter = AFNS(
            alphabet=alphabet,
            etats={etat_initial},
            etat_initial=etat_initial,
            etats_finaux={etat_initial} if etat_initial.est_final else set()
        )
        
        etat_map = {(ad1.etat_initial, ad2.etat_initial): etat_initial}
        queue = [(ad1.etat_initial, ad2.etat_initial)]
        visited = set()
        
        while queue:
            etat1, etat2 = queue.pop(0)
            if (etat1, etat2) in visited:
                continue
            visited.add((etat1, etat2))
            
            etat_source = etat_map[(etat1, etat2)]
            
            for symbole in alphabet:
                for dest1 in ad1.transitions.get(etat1, {}).get(symbole, set()):
                    for dest2 in ad2.transitions.get(etat2, {}).get(symbole, set()):
                        if (dest1, dest2) not in etat_map:
                            etat_dest = Etat(f"({dest1.nom},{dest2.nom})")
                            etat_dest.est_final = (dest1 in ad1.etats_finaux and dest2 in ad2.etats_finaux)
                            
                            etat_map[(dest1, dest2)] = etat_dest
                            automate_inter.etats.add(etat_dest)
                            
                            if etat_dest.est_final:
                                automate_inter.etats_finaux.add(etat_dest)
                            
                            queue.append((dest1, dest2))
                        
                        automate_inter.ajouter_transition(etat_source, symbole, etat_map[(dest1, dest2)])
        
        return automate_inter


    # 1. Simplifier _generer_nom_etat et _reinitialiser_compteur
    def _generer_nom_etat(self, prefix: str = "q") -> str:
        """Génère un nom d'état unique"""
        nom = f"{prefix}{self.compteur_etats}"
        self.compteur_etats += 1
        return nom


    # 2. Simplifier construire_automate_glushkov - éliminer variables intermédiaires
    @classmethod
    def construire_automate_glushkov(cls, regex: str) -> 'AD':
        """Construction de Glushkov optimisée"""
        parser = cls()
        parser.expression = regex
        parser.position = 0
        parser.compteur_etats = 0
        
        est_valide, message = cls.valider_syntaxe(regex)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        ast = parser._construire_ast()
        props = cls._compute_ast_properties(ast)
        
        etat_initial = Etat("q0")
        etats = {etat_initial}
        pos_to_etat = {pos: Etat(f"q{pos}") for pos, symbole in props.positions.items() if symbole != '#'}
        etats.update(pos_to_etat.values())
        
        alphabet = {sym for sym in props.positions.values() if sym != '#'}
        transitions = {}
        
        # Transitions depuis l'état initial
        for symbole in alphabet:
            destinations = {pos_to_etat[pos] for pos in props.first 
                        if props.positions.get(pos) == symbole and pos in pos_to_etat}
            if destinations:
                transitions.setdefault(etat_initial, {})[symbole] = destinations
        
        # Transitions entre positions
        for pos, symbole in props.positions.items():
            if symbole != '#' and pos in pos_to_etat:
                etat_source = pos_to_etat[pos]
                for follow_pos in props.follow.get(pos, set()):
                    follow_symbole = props.positions.get(follow_pos)
                    if follow_symbole and follow_symbole != '#' and follow_pos in pos_to_etat:
                        transitions.setdefault(etat_source, {}).setdefault(
                            follow_symbole, set()).add(pos_to_etat[follow_pos])
        
        # États finaux
        etats_finaux = set()
        if props.nullable:
            etats_finaux.add(etat_initial)
        etats_finaux.update(pos_to_etat[pos] for pos in props.last if pos in pos_to_etat)
        
        automate = AD(
            alphabet=alphabet,
            etats=etats,
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        automate.transitions = transitions
        return automate

    # 3. Simplifier construire_automate_thompson
    @classmethod
    def construire_automate_thompson(cls, expression: str) -> 'AFNS':
        """Construction de Thompson optimisée"""
        parser = cls()
        parser.expression = expression
        parser.position = 0
        parser.compteur_etats = 0
        parser._transitions = {}
        
        ast = parser._parser_expression_ast()
        initial, final = parser._build_thompson(ast)
        
        etats = parser._collect_states(initial)
        alphabet = parser._collect_alphabet(ast)
        
        automate = AFNS(
            alphabet=alphabet,
            etats=etats,
            etat_initial=initial,
            etats_finaux={final}
        )
        automate.transitions = parser._transitions
        return automate

    # 5. Simplifier construire_plus (utiliser la construction directe)
    def construire_plus(self, automate: 'AFNS') -> 'AFNS':
        """Construction directe pour A+"""
        auto_copy = self._copier_automate(automate)
        
        # Ajouter transitions de retour depuis les états finaux vers l'initial
        for etat_final in list(auto_copy.etats_finaux):
            auto_copy.ajouter_transition_epsilon(etat_final, auto_copy.etat_initial)
        
        return auto_copy

    # 6. Simplifier construire_intersection - éliminer variables temporaires
    def construire_intersection(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        """Construction d'intersection par produit cartésien"""
        ad1 = auto1.determiniser() if hasattr(auto1, 'determiniser') else auto1
        ad2 = auto2.determiniser() if hasattr(auto2, 'determiniser') else auto2
        
        alphabet = ad1.alphabet & ad2.alphabet
        etat_initial = Etat(f"({ad1.etat_initial.nom},{ad2.etat_initial.nom})")
        etat_initial.est_final = (ad1.etat_initial in ad1.etats_finaux and 
                                ad2.etat_initial in ad2.etats_finaux)
        
        automate_inter = AFNS(
            alphabet=alphabet,
            etats={etat_initial},
            etat_initial=etat_initial,
            etats_finaux={etat_initial} if etat_initial.est_final else set()
        )
        
        etat_map = {(ad1.etat_initial, ad2.etat_initial): etat_initial}
        queue = [(ad1.etat_initial, ad2.etat_initial)]
        visited = set()
        
        while queue:
            etat1, etat2 = queue.pop(0)
            if (etat1, etat2) in visited:
                continue
            visited.add((etat1, etat2))
            
            etat_source = etat_map[(etat1, etat2)]
            
            for symbole in alphabet:
                for dest1 in ad1.transitions.get(etat1, {}).get(symbole, set()):
                    for dest2 in ad2.transitions.get(etat2, {}).get(symbole, set()):
                        if (dest1, dest2) not in etat_map:
                            etat_dest = Etat(f"({dest1.nom},{dest2.nom})")
                            etat_dest.est_final = (dest1 in ad1.etats_finaux and dest2 in ad2.etats_finaux)
                            
                            etat_map[(dest1, dest2)] = etat_dest
                            automate_inter.etats.add(etat_dest)
                            
                            if etat_dest.est_final:
                                automate_inter.etats_finaux.add(etat_dest)
                            
                            queue.append((dest1, dest2))
                        
                        automate_inter.ajouter_transition(etat_source, symbole, etat_map[(dest1, dest2)])
        
        return automate_inter

    # 7. Simplifier parser_regex
    def parser_regex(self, expression: str) -> 'AFNS':
        """Parse une regex et retourne l'automate équivalent"""
        self.expression = expression
        self.position = 0
        self.compteur_etats = 0
        
        est_valide, message = RegexParser.valider_syntaxe(expression)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        return self._parser_expression()

    # 8. Simplifier cloturer_regex_par_intersection
    @classmethod
    def cloturer_regex_par_intersection(cls, regexes: List[str]) -> 'AFNS':
        """Calcule la clôture par intersection d'une liste d'expressions régulières"""
        if not regexes:
            raise ValueError("La liste d'expressions régulières ne peut pas être vide")
        
        parser = cls()
        automates = [parser.parser_regex(regex) for regex in regexes]
        return parser.cloturer_par_intersection(automates)

    # 9. Simplifier construire_union - éliminer copie de transitions redondante
    def construire_union(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        auto1_copy = self._copier_automate(auto1)
        auto2_copy = self._copier_automate(auto2)

        nouvel_initial = Etat(self._generer_nom_etat())
        nouvel_final = Etat(self._generer_nom_etat(), est_final=True)

        etats = {nouvel_initial, nouvel_final}
        etats.update(auto1_copy.etats)
        etats.update(auto2_copy.etats)

        # Désactiver anciens états finaux
        for etat in auto1_copy.etats_finaux | auto2_copy.etats_finaux:
            etat.est_final = False

        automate = AFNS(
            alphabet=auto1_copy.alphabet | auto2_copy.alphabet,
            etats=etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )

        # Copier toutes les transitions en une fois
        for auto_copy in [auto1_copy, auto2_copy]:
            for source, trans in auto_copy.transitions.items():
                for symbole, destinations in trans.items():
                    for dest in destinations:
                        automate.ajouter_transition(source, symbole, dest)

        # Ajouter ε-transitions
        automate.ajouter_transition_epsilon(nouvel_initial, auto1_copy.etat_initial)
        automate.ajouter_transition_epsilon(nouvel_initial, auto2_copy.etat_initial)

        for etat_final in auto1_copy.etats_finaux | auto2_copy.etats_finaux:
            automate.ajouter_transition_epsilon(etat_final, nouvel_final)

        return automate

    # 10. Simplifier construire_optionnel - regrouper ajouts ε-transitions
    def construire_optionnel(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'automate pour l'opération optionnelle (?)"""
        auto_copy = self._copier_automate(automate)
        
        nouvel_initial = Etat(self._generer_nom_etat())
        nouvel_final = Etat(self._generer_nom_etat(), est_final=True)
        
        etats = {nouvel_initial, nouvel_final}
        etats.update(auto_copy.etats)
        
        # Désactiver anciens états finaux
        for etat in auto_copy.etats_finaux:
            etat.est_final = False
        
        automate_opt = AFNS(
            alphabet=auto_copy.alphabet,
            etats=etats,
            etat_initial=nouvel_initial,
            etats_finaux={nouvel_final}
        )
        
        # Copier transitions
        for source, trans in auto_copy.transitions.items():
            for symbole, destinations in trans.items():
                for dest in destinations:
                    automate_opt.ajouter_transition(source, symbole, dest)
        
        # Ajouter toutes les ε-transitions
        automate_opt.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        automate_opt.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        for etat_final in auto_copy.etats_finaux:
            automate_opt.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        return automate_opt