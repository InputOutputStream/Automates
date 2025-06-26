from typing import Tuple, Dict, Set, List
import copy
from ..Automate import Automate, AFNS, AD
from ..Etat import Etat
 
class RegexNode:
    """Représente un nœud dans l'arbre syntaxique de la regex"""
    pass

class SymbolNode(RegexNode):
    def __init__(self, symbol: str):
        self.symbol = symbol

class ConcatNode(RegexNode):
    def __init__(self, left: RegexNode, right: RegexNode):
        self.left = left
        self.right = right

class UnionNode(RegexNode):
    def __init__(self, left: RegexNode, right: RegexNode):
        self.left = left
        self.right = right

class StarNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child

class PlusNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child

class OptionalNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child


class RegexParser:
    """
    Parseur d'expressions régulières utilisant l'algorithme de Thompson
    """
    
    def __init__(self):
        """Initialise le parseur"""
        self.position = 0
        self.expression = ""
        self.compteur_etats = 0  # Compteur global pour les noms d'états
        
    def _generer_nom_etat(self, prefix: str = "q") -> str:
        """Génère un nom d'état unique et simple"""
        nom = f"{prefix}{self.compteur_etats}"
        self.compteur_etats += 1
        return nom
    
    def _reinitialiser_compteur(self):
        """Remet le compteur d'états à zéro"""
        self.compteur_etats = 0
        
    def parser_regex(self, expression: str) -> 'AFNS':
        """Parse une regex et retourne l'automate équivalent"""
        self.expression = expression
        self.position = 0
        self._reinitialiser_compteur()  # Réinitialiser pour chaque nouvelle regex
        
        # Validation de la syntaxe
        est_valide, message = RegexParser.valider_syntaxe(expression)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        # Parsing et construction de l'automate
        automate = self._parser_expression()
        return automate
    
    @classmethod
    def construire_automate_glushkov(cls, regex: str) -> 'AD':
        """
        Construction d'automate par la méthode de Glushkov.
        Produit directement un automate déterministe sans ε-transitions.
        """
        # Créer une instance temporaire pour parser
        parser = cls()
        
        # Étape 1: Construire l'AST de la regex
        parser.expression = regex
        parser.position = 0
        parser._reinitialiser_compteur()
        
        # Validation
        est_valide, message = parser.valider_syntaxe(regex)
        if not est_valide:
            raise ValueError(f"Syntaxe invalide: {message}")
        
        # Construire l'AST
        ast = parser._construire_ast()
        
        # Étape 2: Calculer les positions et les ensembles
        positions = cls._calculer_positions(ast)
        alphabet = cls._extraire_alphabet(positions)
        
        first_pos = cls._calculer_first(ast, positions)
        last_pos = cls._calculer_last(ast, positions)
        follow_pos = cls._calculer_follow(ast, positions)
        nullable = cls._calculer_nullable(ast)
        
        # Étape 3: Construire l'automate avec des noms simples
        etat_initial = Etat("q0")
        etats = {etat_initial}
        
        # Créer un état pour chaque position
        pos_vers_etat = {}
        compteur_etat = 1
        for pos in positions:
            if positions[pos] != '#':  # Exclure le marqueur de fin
                etat = Etat(f"q{compteur_etat}")
                etats.add(etat)
                pos_vers_etat[pos] = etat
                compteur_etat += 1
        
        # Construire les transitions
        transitions = {}
        transitions[etat_initial] = {}
        
        # Transitions depuis l'état initial
        for symbole in alphabet:
            destinations = set()
            for pos in first_pos:
                if pos in positions and positions[pos] == symbole:
                    destinations.add(pos_vers_etat[pos])
            if destinations:
                if symbole not in transitions[etat_initial]:
                    transitions[etat_initial][symbole] = set()
                transitions[etat_initial][symbole].update(destinations)
        
        # Transitions entre états
        for pos in positions:
            if positions[pos] == '#' or pos not in pos_vers_etat:
                continue
                
            etat_source = pos_vers_etat[pos]
            if etat_source not in transitions:
                transitions[etat_source] = {}
            
            for symbole in alphabet:
                destinations = set()
                for pos_suiv in follow_pos.get(pos, set()):
                    if pos_suiv in positions and positions[pos_suiv] == symbole:
                        destinations.add(pos_vers_etat[pos_suiv])
                if destinations:
                    if symbole not in transitions[etat_source]:
                        transitions[etat_source][symbole] = set()
                    transitions[etat_source][symbole].update(destinations)
        
        # États finaux
        etats_finaux = set()
        if nullable:  # Si la regex accepte le mot vide
            etats_finaux.add(etat_initial)
        
        # Ajouter les états correspondant aux positions dans Last
        for pos in last_pos:
            if pos in pos_vers_etat:
                etats_finaux.add(pos_vers_etat[pos])
        
        # Créer l'automate
        automate = AD(
            alphabet=alphabet,
            etats=etats,
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        automate.transitions = transitions
        
        return automate

    def _construire_ast(self) -> RegexNode:
        """Construit l'AST de la regex"""
        return self._parser_expression_ast()

    def _parser_expression_ast(self) -> RegexNode:
        """Parse une expression et retourne l'AST (gère l'union |)"""
        gauche = self._parser_terme_ast()
        
        while self.position < len(self.expression) and self.expression[self.position] == '|':
            self.position += 1  # Passer le '|'
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
            self.position += 1  # Passer '('
            expr = self._parser_expression_ast()
            if self.position >= len(self.expression) or self.expression[self.position] != ')':
                raise ValueError("Parenthèse fermante manquante")
            self.position += 1  # Passer ')'
            return expr
        else:
            self.position += 1
            return SymbolNode(char)

    @staticmethod
    def _calculer_positions(ast: RegexNode) -> Dict[int, str]:
        """Calcule les positions des symboles dans l'AST"""
        positions = {}
        counter = [1]  # Utiliser une liste pour la mutabilité
        
        def parcourir(node: RegexNode):
            if isinstance(node, SymbolNode):
                positions[counter[0]] = node.symbol
                counter[0] += 1
            elif isinstance(node, (ConcatNode, UnionNode)):
                parcourir(node.left)
                parcourir(node.right)
            elif isinstance(node, (StarNode, PlusNode, OptionalNode)):
                parcourir(node.child)
        
        # Ajouter le marqueur de fin
        parcourir(ast)
        positions[counter[0]] = '#'
        
        return positions

    @staticmethod
    def _extraire_alphabet(positions: Dict[int, str]) -> Set[str]:
        """Extrait l'alphabet des positions"""
        alphabet = set()
        for symbole in positions.values():
            if symbole != '#':
                alphabet.add(symbole)
        return alphabet

    @staticmethod
    def _calculer_first(ast: RegexNode, positions: Dict[int, str]) -> Set[int]:
        """Calcule l'ensemble First de l'AST"""
        def first_rec(node: RegexNode) -> Tuple[Set[int], int]:
            """Retourne (first_set, nombre_de_positions_consommées)"""
            if isinstance(node, SymbolNode):
                return {1}, 1
            elif isinstance(node, ConcatNode):
                left_first, left_count = first_rec(node.left)
                right_first, right_count = first_rec(node.right)
                # Ajuster les positions de droite
                right_first_adjusted = {pos + left_count for pos in right_first}
                
                if RegexParser._nullable_rec(node.left):
                    return left_first | right_first_adjusted, left_count + right_count
                else:
                    return left_first, left_count + right_count
            elif isinstance(node, UnionNode):
                left_first, left_count = first_rec(node.left)
                right_first, right_count = first_rec(node.right)
                # Ajuster les positions de droite
                right_first_adjusted = {pos + left_count for pos in right_first}
                return left_first | right_first_adjusted, left_count + right_count
            elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
                child_first, child_count = first_rec(node.child)
                return child_first, child_count
            return set(), 0
        
        first_set, _ = first_rec(ast)
        return first_set

    @staticmethod
    def _calculer_last(ast: RegexNode, positions: Dict[int, str]) -> Set[int]:
        """Calcule l'ensemble Last de l'AST"""
        def last_rec(node: RegexNode) -> Tuple[Set[int], int]:
            """Retourne (last_set, nombre_de_positions_consommées)"""
            if isinstance(node, SymbolNode):
                return {1}, 1
            elif isinstance(node, ConcatNode):
                left_last, left_count = last_rec(node.left)
                right_last, right_count = last_rec(node.right)
                # Ajuster les positions de droite
                right_last_adjusted = {pos + left_count for pos in right_last}
                
                if RegexParser._nullable_rec(node.right):
                    return left_last | right_last_adjusted, left_count + right_count
                else:
                    return right_last_adjusted, left_count + right_count
            elif isinstance(node, UnionNode):
                left_last, left_count = last_rec(node.left)
                right_last, right_count = last_rec(node.right)
                # Ajuster les positions de droite
                right_last_adjusted = {pos + left_count for pos in right_last}
                return left_last | right_last_adjusted, left_count + right_count
            elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
                child_last, child_count = last_rec(node.child)
                return child_last, child_count
            return set(), 0
        
        last_set, _ = last_rec(ast)
        return last_set

    @staticmethod
    def _calculer_follow(ast: RegexNode, positions: Dict[int, str]) -> Dict[int, Set[int]]:
        """Calcule l'ensemble Follow pour chaque position"""
        follow = {pos: set() for pos in positions.keys()}
        
        def follow_rec(node: RegexNode, offset: int = 0):
            """Calcule follow avec un offset pour les positions"""
            if isinstance(node, SymbolNode):
                return 1  # Retourne le nombre de positions consommées
            elif isinstance(node, ConcatNode):
                # Calculer d'abord les positions pour les sous-arbres
                left_consumed = follow_rec(node.left, offset)
                right_consumed = follow_rec(node.right, offset + left_consumed)
                
                # Pour la concaténation: Last(left) -> First(right)
                left_last = RegexParser._calculer_last_with_offset(node.left, offset)
                right_first = RegexParser._calculer_first_with_offset(node.right, offset + left_consumed)
                
                for pos in left_last:
                    if pos in follow:  # Vérifier que la position existe
                        follow[pos].update(right_first)
                
                return left_consumed + right_consumed
            elif isinstance(node, UnionNode):
                left_consumed = follow_rec(node.left, offset)
                right_consumed = follow_rec(node.right, offset + left_consumed)
                return left_consumed + right_consumed
            elif isinstance(node, StarNode):
                child_consumed = follow_rec(node.child, offset)
                
                # Pour l'étoile: Last(child) -> First(child)
                child_last = RegexParser._calculer_last_with_offset(node.child, offset)
                child_first = RegexParser._calculer_first_with_offset(node.child, offset)
                
                for pos in child_last:
                    if pos in follow:  # Vérifier que la position existe
                        follow[pos].update(child_first)
                
                return child_consumed
            elif isinstance(node, PlusNode):
                child_consumed = follow_rec(node.child, offset)
                
                # A+ = AA*, donc Last(A) -> First(A)
                child_last = RegexParser._calculer_last_with_offset(node.child, offset)
                child_first = RegexParser._calculer_first_with_offset(node.child, offset)
                
                for pos in child_last:
                    if pos in follow:  # Vérifier que la position existe
                        follow[pos].update(child_first)
                
                return child_consumed
            elif isinstance(node, OptionalNode):
                return follow_rec(node.child, offset)
            
            return 0
        
        follow_rec(ast, 0)
        return follow

    @staticmethod
    def _calculer_first_with_offset(node: RegexNode, offset: int) -> Set[int]:
        """Calcule First avec un offset pour les positions"""
        def first_rec(node: RegexNode, current_offset: int) -> Tuple[Set[int], int]:
            if isinstance(node, SymbolNode):
                return {current_offset + 1}, 1
            elif isinstance(node, ConcatNode):
                left_first, left_count = first_rec(node.left, current_offset)
                right_first, right_count = first_rec(node.right, current_offset + left_count)
                
                if RegexParser._nullable_rec(node.left):
                    return left_first | right_first, left_count + right_count
                else:
                    return left_first, left_count + right_count
            elif isinstance(node, UnionNode):
                left_first, left_count = first_rec(node.left, current_offset)
                right_first, right_count = first_rec(node.right, current_offset + left_count)
                return left_first | right_first, left_count + right_count
            elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
                return first_rec(node.child, current_offset)
            return set(), 0
        
        first_set, _ = first_rec(node, offset)
        return first_set

    @staticmethod
    def _calculer_last_with_offset(node: RegexNode, offset: int) -> Set[int]:
        """Calcule Last avec un offset pour les positions"""
        def last_rec(node: RegexNode, current_offset: int) -> Tuple[Set[int], int]:
            if isinstance(node, SymbolNode):
                return {current_offset + 1}, 1
            elif isinstance(node, ConcatNode):
                left_last, left_count = last_rec(node.left, current_offset)
                right_last, right_count = last_rec(node.right, current_offset + left_count)
                
                if RegexParser._nullable_rec(node.right):
                    return left_last | right_last, left_count + right_count
                else:
                    return right_last, left_count + right_count
            elif isinstance(node, UnionNode):
                left_last, left_count = last_rec(node.left, current_offset)
                right_last, right_count = last_rec(node.right, current_offset + left_count)
                return left_last | right_last, left_count + right_count
            elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
                return last_rec(node.child, current_offset)
            return set(), 0
        
        last_set, _ = last_rec(node, offset)
        return last_set

    @staticmethod
    def _calculer_nullable(ast: RegexNode) -> bool:
        """Calcule si l'AST peut générer le mot vide"""
        return RegexParser._nullable_rec(ast)

    @staticmethod
    def _nullable_rec(node: RegexNode) -> bool:
        """Version récursive de nullable"""
        if isinstance(node, SymbolNode):
            return False
        elif isinstance(node, ConcatNode):
            return RegexParser._nullable_rec(node.left) and RegexParser._nullable_rec(node.right)
        elif isinstance(node, UnionNode):
            return RegexParser._nullable_rec(node.left) or RegexParser._nullable_rec(node.right)
        elif isinstance(node, (StarNode, OptionalNode)):
            return True
        elif isinstance(node, PlusNode):
            return RegexParser._nullable_rec(node.child)
        return False

    @staticmethod
    def _first_rec(node: RegexNode, pos_counter: List[int]) -> Set[int]:
        """Version récursive de first avec compteur de position"""
        if isinstance(node, SymbolNode):
            result = {pos_counter[0]}
            pos_counter[0] += 1
            return result
        elif isinstance(node, ConcatNode):
            left_first = RegexParser._first_rec(node.left, pos_counter)
            if RegexParser._nullable_rec(node.left):
                right_first = RegexParser._first_rec(node.right, pos_counter)
                return left_first | right_first
            else:
                # Consommer les positions de right même si on ne les utilise pas
                RegexParser._first_rec(node.right, pos_counter)
                return left_first
        elif isinstance(node, UnionNode):
            left_first = RegexParser._first_rec(node.left, pos_counter)
            right_first = RegexParser._first_rec(node.right, pos_counter)
            return left_first | right_first
        elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
            return RegexParser._first_rec(node.child, pos_counter)
        return set()

    @staticmethod
    def _last_rec(node: RegexNode, pos_counter: List[int]) -> Set[int]:
        """Version récursive de last avec compteur de position"""
        if isinstance(node, SymbolNode):
            result = {pos_counter[0]}
            pos_counter[0] += 1
            return result
        elif isinstance(node, ConcatNode):
            left_last = RegexParser._last_rec(node.left, pos_counter)
            right_last = RegexParser._last_rec(node.right, pos_counter)
            if RegexParser._nullable_rec(node.right):
                return left_last | right_last
            else:
                return right_last
        elif isinstance(node, UnionNode):
            left_last = RegexParser._last_rec(node.left, pos_counter)
            right_last = RegexParser._last_rec(node.right, pos_counter)
            return left_last | right_last
        elif isinstance(node, (StarNode, OptionalNode, PlusNode)):
            return RegexParser._last_rec(node.child, pos_counter)
        return set()

    @classmethod
    def construire_automate_thompson(cls, expression: str) -> 'AFNS':
        """
        Construit un automate fini non-déterministe à partir d'une expression régulière
        en utilisant l'algorithme de Thompson.
        
        Args:
            expression (str): Expression régulière à convertir
            
        Returns:
            AFNS: Automate fini non-déterministe équivalent
            
        Raises:
            ValueError: Si l'expression régulière est invalide
        """
        try:
            # Créer une instance pour utiliser les méthodes d'instance
            parser = cls()
            automate = parser.parser_regex(expression)
            
            return automate
            
        except ValueError as e:
            raise ValueError(f"Erreur lors de la construction de l'automate Thompson: {e}")
        except Exception as e:
            raise ValueError(f"Erreur inattendue lors du parsing: {e}")
    
    @classmethod
    def valider_syntaxe(cls, expression: str) -> Tuple[bool, str]:
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
        
        # Vérification des doubles opérateurs
        for i in range(len(expression) - 1):
            if expression[i] in '*+?' and expression[i+1] in '*+?':
                return False, f"Opérateurs consécutifs à la position {i}"
        
        # Vérification des alternations vides
        for i, char in enumerate(expression):
            if char == '|':
                if i == 0 or i == len(expression) - 1:
                    return False, f"Alternation vide à la position {i}"
                if expression[i-1] == '(' or expression[i+1] == ')':
                    return False, f"Alternation vide à la position {i}"
                if expression[i-1] == '|' or expression[i+1] == '|':
                    return False, f"Alternations consécutives à la position {i}"
        
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
        # 1. Du nouvel initial vers l'ancien initial
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        
        # 2. Du nouvel initial vers le nouvel final (pour accepter ε)
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        # 3. Des anciens finaux vers le nouvel final
        for etat_final in auto_copy.etats_finaux:
            automate_etoile.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        # 4. Des anciens finaux vers l'ancien initial (pour la répétition)
        for etat_final in auto_copy.etats_finaux:
            automate_etoile.ajouter_transition_epsilon(etat_final, auto_copy.etat_initial)
        
        return automate_etoile
    
    def construire_plus(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'automate pour l'opération plus (+)"""
        # A+ = AA*
        auto_copy = self._copier_automate(automate)
        etoile = self.construire_etoile(automate)
        
        return self.construire_concatenation(auto_copy, etoile)
    
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
        # 1. Du nouvel initial vers l'ancien initial
        automate_opt.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        
        # 2. Du nouvel initial vers le nouvel final (pour accepter ε)
        automate_opt.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        # 3. Des anciens finaux vers le nouvel final
        for etat_final in auto_copy.etats_finaux:
            automate_opt.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        return automate_opt
    
    def construire_intersection(self, auto1: 'AFNS', auto2: 'AFNS') -> 'AFNS':
        """
        Construit l'automate pour l'intersection de deux automates.
        Utilise la construction par produit cartésien des états.
        """
        # Convertir en automate déterministe si nécessaire pour simplifier l'intersection
        ad1 = auto1.determiniser() if hasattr(auto1, 'determiniser') else auto1
        ad2 = auto2.determiniser() if hasattr(auto2, 'determiniser') else auto2
        
        # Alphabet de l'intersection
        alphabet = ad1.alphabet & ad2.alphabet
        
        # États : produit cartésien des états des deux automates
        etats = set()
        etat_map = {}  # Pour mapper (état1, état2) -> nouvel_état
        
        # État initial : produit des états initiaux
        nom_initial = f"({ad1.etat_initial.nom},{ad2.etat_initial.nom})"
        etat_initial = Etat(nom_initial)
        
        # Un état est final si les deux états composants sont finaux
        est_final_initial = (ad1.etat_initial in ad1.etats_finaux and 
                           ad2.etat_initial in ad2.etats_finaux)
        etat_initial.est_final = est_final_initial
        
        etats.add(etat_initial)
        etat_map[(ad1.etat_initial, ad2.etat_initial)] = etat_initial
        
        # Construction de l'automate intersection
        automate_inter = AFNS(
            alphabet=alphabet,
            etats={etat_initial},
            etat_initial=etat_initial,
            etats_finaux=set()
        )
        
        if est_final_initial:
            automate_inter.etats_finaux.add(etat_initial)
        
        # File pour explorer les états
        etats_a_explorer = [(ad1.etat_initial, ad2.etat_initial)]
        etats_explores = set()
        
        while etats_a_explorer:
            etat1, etat2 = etats_a_explorer.pop(0)
            
            if (etat1, etat2) in etats_explores:
                continue
            etats_explores.add((etat1, etat2))
            
            etat_source = etat_map[(etat1, etat2)]
            
            # Pour chaque symbole de l'alphabet commun
            for symbole in alphabet:
                # Destinations depuis etat1 avec symbole
                dest1_set = set()
                if etat1 in ad1.transitions and symbole in ad1.transitions[etat1]:
                    dest1_set = ad1.transitions[etat1][symbole]
                
                # Destinations depuis etat2 avec symbole
                dest2_set = set()
                if etat2 in ad2.transitions and symbole in ad2.transitions[etat2]:
                    dest2_set = ad2.transitions[etat2][symbole]
                
                # Produit cartésien des destinations
                for dest1 in dest1_set:
                    for dest2 in dest2_set:
                        # Créer l'état destination s'il n'existe pas
                        if (dest1, dest2) not in etat_map:
                            nom_dest = f"({dest1.nom},{dest2.nom})"
                            etat_dest = Etat(nom_dest)
                            
                            # Final si les deux composants sont finaux
                            est_final_dest = (dest1 in ad1.etats_finaux and 
                                            dest2 in ad2.etats_finaux)
                            etat_dest.est_final = est_final_dest
                            
                            etat_map[(dest1, dest2)] = etat_dest
                            automate_inter.etats.add(etat_dest)
                            
                            if est_final_dest:
                                automate_inter.etats_finaux.add(etat_dest)
                            
                            # Ajouter à la file d'exploration
                            etats_a_explorer.append((dest1, dest2))
                        
                        etat_dest = etat_map[(dest1, dest2)]
                        
                        # Ajouter la transition
                        automate_inter.ajouter_transition(etat_source, symbole, etat_dest)
        
        return automate_inter
    
    @classmethod
    def construire_intersection_regex(cls, regex1: str, regex2: str) -> 'AFNS':
        """
        Construit l'automate pour l'intersection de deux expressions régulières.
        
        Args:
            regex1 (str): Première expression régulière
            regex2 (str): Deuxième expression régulière
            
        Returns:
            AFNS: Automate représentant l'intersection des deux langages
        """
        parser = cls()
        
        # Construire les automates pour chaque regex
        auto1 = parser.parser_regex(regex1)
        auto2 = parser.parser_regex(regex2)
        
        # Construire l'intersection
        return parser.construire_intersection(auto1, auto2)
    
    def cloturer_par_intersection(self, automates: List['AFNS']) -> 'AFNS':
        """
        Calcule la clôture par intersection d'une liste d'automates.
        Retourne l'automate représentant l'intersection de tous les automates donnés.
        
        Args:
            automates (List[AFNS]): Liste des automates à intersecter
            
        Returns:
            AFNS: Automate représentant l'intersection de tous les automates
            
        Raises:
            ValueError: Si la liste est vide
        """
        if not automates:
            raise ValueError("La liste d'automates ne peut pas être vide")
        
        if len(automates) == 1:
            return self._copier_automate(automates[0])
        
        # Commencer avec le premier automate
        resultat = self._copier_automate(automates[0])
        
        # Intersecter successivement avec tous les autres
        for i in range(1, len(automates)):
            resultat = self.construire_intersection(resultat, automates[i])
        
        return resultat
    
    @classmethod
    def cloturer_regex_par_intersection(cls, regexes: List[str]) -> 'AFNS':
        """
        Calcule la clôture par intersection d'une liste d'expressions régulières.
        
        Args:
            regexes (List[str]): Liste des expressions régulières
            
        Returns:
            AFNS: Automate représentant l'intersection de tous les langages
        """
        if not regexes:
            raise ValueError("La liste d'expressions régulières ne peut pas être vide")
        
        parser = cls()
        
        # Construire les automates pour chaque regex
        automates = []
        for regex in regexes:
            automate = parser.parser_regex(regex)
            automates.append(automate)
        
        # Calculer la clôture par intersection
        return parser.cloturer_par_intersection(automates)
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
        # 1. Du nouvel initial vers l'ancien initial
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        
        # 2. Du nouvel initial vers le nouvel final (pour accepter ε)
        automate_etoile.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        # 3. Des anciens finaux vers le nouvel final
        for etat_final in auto_copy.etats_finaux:
            automate_etoile.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        # 4. Des anciens finaux vers l'ancien initial (pour la répétition)
        for etat_final in auto_copy.etats_finaux:
            automate_etoile.ajouter_transition_epsilon(etat_final, auto_copy.etat_initial)
        
        return automate_etoile
    
    def construire_plus(self, automate: 'AFNS') -> 'AFNS':
        """Construit l'automate pour l'opération plus (+)"""
        # A+ = AA*
        auto_copy = self._copier_automate(automate)
        etoile = self.construire_etoile(automate)
        
        return self.construire_concatenation(auto_copy, etoile)
    
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
        # 1. Du nouvel initial vers l'ancien initial
        automate_opt.ajouter_transition_epsilon(nouvel_initial, auto_copy.etat_initial)
        
        # 2. Du nouvel initial vers le nouvel final (pour accepter ε)
        automate_opt.ajouter_transition_epsilon(nouvel_initial, nouvel_final)
        
        # 3. Des anciens finaux vers le nouvel final
        for etat_final in auto_copy.etats_finaux:
            automate_opt.ajouter_transition_epsilon(etat_final, nouvel_final)
        
        return automate_opt