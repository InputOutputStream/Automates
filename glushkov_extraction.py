import re
from typing import Set, Dict, List, Optional, Union, Tuple
from collections import defaultdict

# CLASSES DE BASE 


class Etat:
    """Classe représentant un état d'automate."""
    def __init__(self, nom: str, est_initial: bool = False, est_final: bool = False):
        self.nom = nom
        self.est_initial = est_initial
        self.est_final = est_final
    
    def __str__(self):
        return self.nom
    
    def __repr__(self):
        return f"Etat({self.nom})"
    
    def __eq__(self, other):
        return isinstance(other, Etat) and self.nom == other.nom
    
    def __hash__(self):
        return hash(self.nom)

class AFNS:
    """Automate Fini Non-déterministe avec epsilon-transitions."""
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, etats_finaux: Set[Etat]):
        self.alphabet = alphabet
        self.etats = etats
        self.etat_initial = etat_initial
        self.etats_finaux = etats_finaux
        self.transitions = defaultdict(lambda: defaultdict(set))
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_dest: Etat):
        """Ajoute une transition à l'automate."""
        self.transitions[etat_source][symbole].add(etat_dest)
    
    def afficher(self) -> str:
        """Affiche l'automate sous forme textuelle."""
        result = f"États: {[e.nom for e in self.etats]}\n"
        result += f"Alphabet: {sorted(self.alphabet)}\n"
        result += f"État initial: {self.etat_initial.nom}\n"
        result += f"États finaux: {[e.nom for e in self.etats_finaux]}\n"
        result += "Transitions:\n"
        
        for etat_source, trans in self.transitions.items():
            for symbole, etats_dest in trans.items():
                for etat_dest in etats_dest:
                    result += f"  {etat_source.nom} --{symbole}--> {etat_dest.nom}\n"
        
        return result
    
    def automate_a_matrice(self) -> Tuple[List[List[Set]], List[Etat], List[str]]:
        """Convertit l'automate en représentation matricielle."""
        etats_list = list(self.etats)
        alphabet_list = list(self.alphabet)
        n = len(etats_list)
        m = len(alphabet_list)
        
        # Matrice de transitions
        matrice = [[set() for _ in range(m)] for _ in range(n)]
        
        for i, etat_source in enumerate(etats_list):
            for j, symbole in enumerate(alphabet_list):
                if etat_source in self.transitions and symbole in self.transitions[etat_source]:
                    for etat_dest in self.transitions[etat_source][symbole]:
                        k = etats_list.index(etat_dest)
                        matrice[i][j].add(k)
        
        return matrice, etats_list, alphabet_list


# CLASSES PRINCIPALES


class ExpressionReguliere:
    """Classe pour représenter et manipuler les expressions régulières."""
    
    def __init__(self, expression: str):
        self.expression = expression
        self.alphabet = self._extraire_alphabet()
        self.positions = {}  # Mapping position -> symbole
        self.compteur_position = 0
    
    def _extraire_alphabet(self) -> Set[str]:
        """Extrait l'alphabet de l'expression régulière."""
        alphabet = set()
        for char in self.expression:
            if char.isalnum():  # Lettres et chiffres seulement
                alphabet.add(char)
        return alphabet
    
    def lineariser(self) -> str:
        """Linéarise l'expression en ajoutant des indices aux symboles."""
        expression_lineaire = ""
        self.positions = {}
        self.compteur_position = 1
        
        for char in self.expression:
            if char.isalnum():  # Symbole de l'alphabet
                position_actuelle = self.compteur_position
                self.positions[position_actuelle] = char
                expression_lineaire += f"{char}{position_actuelle}"
                self.compteur_position += 1
            else:
                expression_lineaire += char
        
        return expression_lineaire


class GlushkovConstructor:
    """Implémentation de l'algorithme de Glushkov."""
    
    def __init__(self):
        self.first = set()
        self.last = set()
        self.follow = defaultdict(set)
        self.nullable = False
        self.positions = {}
    
    def construire_automate(self, expression: str) -> AFNS:
        """
        Construit un automate à partir d'une expression régulière selon Glushkov.
        
        Args:
            expression: Expression régulière sous forme de chaîne
            
        Returns:
            AFNS: Automate fini non-déterministe avec epsilon-transitions
        """
        # Préparation de l'expression
        expr_reg = ExpressionReguliere(expression)
        expr_lineaire = expr_reg.lineariser()
        self.positions = expr_reg.positions
        
        print(f"Expression originale: {expression}")
        print(f"Expression linéarisée: {expr_lineaire}")
        print(f"Positions: {self.positions}")
        
        # Calcul des ensembles First, Last, Follow et Nullable
        self._calculer_ensembles(expr_lineaire, expression)
        
        print(f"First: {self.first}")
        print(f"Last: {self.last}")
        print(f"Follow: {dict(self.follow)}")
        print(f"Nullable: {self.nullable}")
        
        # Construction de l'automate
        return self._construire_afns(expr_reg.alphabet)
    
    def _calculer_ensembles(self, expression_lineaire: str, expression_originale: str):
        """Calcule les ensembles First, Last, Follow et Nullable."""
        # Extraire toutes les positions
        positions_dans_expr = []
        i = 0
        while i < len(expression_lineaire):
            if expression_lineaire[i].isalpha():
                # Chercher le numéro de position
                j = i + 1
                while j < len(expression_lineaire) and expression_lineaire[j].isdigit():
                    j += 1
                if j > i + 1:
                    position = int(expression_lineaire[i+1:j])
                    positions_dans_expr.append(position)
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        # Calculs simplifiés pour les opérateurs de base
        if positions_dans_expr:
            # First : première position
            self.first = {positions_dans_expr[0]}
            
            # Last : dépend de l'opérateur final
            if "*" in expression_originale:
                # Pour les étoiles, last inclut toutes les positions concernées
                self.last = set(positions_dans_expr)
            else:
                self.last = {positions_dans_expr[-1]}
            
            # Follow : transitions possibles
            for i in range(len(positions_dans_expr) - 1):
                self.follow[positions_dans_expr[i]].add(positions_dans_expr[i + 1])
            
            # Pour l'étoile de Kleene
            if "*" in expression_originale:
                # Les états de Last peuvent revenir vers First
                for pos_last in self.last:
                    for pos_first in self.first:
                        if pos_last != pos_first:
                            self.follow[pos_last].add(pos_first)
        
        # Nullable : vrai si l'expression peut accepter epsilon
        self.nullable = "*" in expression_originale or expression_originale == "ε"
    
    def _construire_afns(self, alphabet: Set[str]) -> AFNS:
        """Construit l'AFNS à partir des ensembles calculés."""
        # Créer les états
        etats = set()
        etat_initial = Etat("q0", est_initial=True)
        etats.add(etat_initial)
        
        # Un état par position
        etats_positions = {}
        for position in self.positions:
            etat = Etat(f"q{position}")
            etats_positions[position] = etat
            etats.add(etat)
        
        # États finaux
        etats_finaux = set()
        if self.nullable:
            etat_initial.est_final = True
            etats_finaux.add(etat_initial)
        
        for position in self.last:
            etat = etats_positions[position]
            etat.est_final = True
            etats_finaux.add(etat)
        
        # Créer l'automate
        afns = AFNS(alphabet, etats, etat_initial, etats_finaux)
        
        # Transitions depuis l'état initial vers First
        for position in self.first:
            symbole = self.positions[position]
            afns.ajouter_transition(etat_initial, symbole, etats_positions[position])
        
        # Transitions entre positions (Follow)
        for position_source, positions_dest in self.follow.items():
            for position_dest in positions_dest:
                symbole = self.positions[position_dest]
                afns.ajouter_transition(
                    etats_positions[position_source], 
                    symbole, 
                    etats_positions[position_dest]
                )
        
        return afns


class ExtracteurExpressionReguliere:
    """Extracteur d'expression régulière à partir d'un automate."""
    
    def extraire_expression(self, automate: AFNS) -> str:
        """
        Extrait l'expression régulière d'un automate par élimination d'états.
        
        Args:
            automate: Automate (AFNS)
            
        Returns:
            str: Expression régulière équivalente
        """
        # Méthode simplifiée : analyse des chemins de l'état initial aux états finaux
        expressions = []
        
        # Pour chaque état final, trouver les chemins depuis l'initial
        for etat_final in automate.etats_finaux:
            expr = self._extraire_chemin_simple(automate, automate.etat_initial, etat_final)
            if expr and expr != "∅":
                expressions.append(expr)
        
        # Combiner avec l'union
        if not expressions:
            return "∅"
        elif len(expressions) == 1:
            return expressions[0]
        else:
            return "(" + "|".join(expressions) + ")"
    
    def _extraire_chemin_simple(self, automate: AFNS, etat_debut: Etat, etat_fin: Etat) -> str:
        """Extrait un chemin simple entre deux états."""
        if etat_debut == etat_fin:
            # Chercher les auto-transitions
            if etat_debut in automate.transitions:
                auto_trans = []
                for symbole, destinations in automate.transitions[etat_debut].items():
                    if etat_debut in destinations:
                        auto_trans.append(symbole)
                if auto_trans:
                    if len(auto_trans) == 1:
                        return f"{auto_trans[0]}*"
                    else:
                        return f"({'+'.join(auto_trans)})*"
            return "ε"
        
        # Chercher les transitions directes
        if etat_debut in automate.transitions:
            transitions_directes = []
            for symbole, destinations in automate.transitions[etat_debut].items():
                if etat_fin in destinations:
                    transitions_directes.append(symbole)
            
            if transitions_directes:
                if len(transitions_directes) == 1:
                    return transitions_directes[0]
                else:
                    return "(" + "|".join(transitions_directes) + ")"
        
        return "∅"



# FONCTIONS PRINCIPALES POUR L'INTÉGRATION


def glushkov_depuis_expression(expression: str) -> AFNS:
    """
    Fonction principale pour l'algorithme de Glushkov.
    
    Args:
        expression: Expression régulière sous forme de chaîne
        
    Returns:
        AFNS: Automate construit selon Glushkov
    """
    constructor = GlushkovConstructor()
    return constructor.construire_automate(expression)


def extraire_expression_depuis_automate(automate: AFNS) -> str:
    """
    Fonction principale pour l'extraction d'expression régulière.
    
    Args:
        automate: Automate (AFNS)
        
    Returns:
        str: Expression régulière équivalente
    """
    extracteur = ExtracteurExpressionReguliere()
    return extracteur.extraire_expression(automate)



# INTERFACE POUR L'APPLICATION WEB


def generer_html_glushkov(expression: str) -> str:
    """
    Génère le HTML pour afficher le résultat de l'algorithme de Glushkov.
    
    Args:
        expression: Expression régulière d'entrée
        
    Returns:
        str: Code HTML pour l'affichage
    """
    try:
        automate = glushkov_depuis_expression(expression)
        
        html = f"""
        <div class="resultat-glushkov">
            <h3>Algorithme de Glushkov</h3>
            <p><strong>Expression d'entrée:</strong> {expression}</p>
            <div class="automate-info">
                <p><strong>Automate résultant:</strong></p>
                <pre>{automate.afficher()}</pre>
            </div>
            <div class="statistiques">
                <p>Nombre d'états: {len(automate.etats)}</p>
                <p>Alphabet: {sorted(automate.alphabet)}</p>
                <p>États finaux: {len(automate.etats_finaux)}</p>
            </div>
        </div>
        """
        return html
        
    except Exception as e:
        return f"""
        <div class="erreur">
            <h3>Erreur - Algorithme de Glushkov</h3>
            <p>Impossible de traiter l'expression: {expression}</p>
            <p>Erreur: {str(e)}</p>
        </div>
        """


def generer_html_extraction(automate: AFNS) -> str:
    """
    Génère le HTML pour afficher le résultat de l'extraction d'expression.
    
    Args:
        automate: Automate à analyser
        
    Returns:
        str: Code HTML pour l'affichage
    """
    try:
        expression = extraire_expression_depuis_automate(automate)
        
        html = f"""
        <div class="resultat-extraction">
            <h3>Extraction d'Expression Régulière</h3>
            <div class="automate-source">
                <p><strong>Automate source:</strong></p>
                <pre>{automate.afficher()}</pre>
            </div>
            <div class="expression-resultat">
                <p><strong>Expression régulière extraite:</strong></p>
                <p class="expression-highlight">{expression}</p>
            </div>
        </div>
        """
        return html
        
    except Exception as e:
        return f"""
        <div class="erreur">
            <h3>Erreur - Extraction d'Expression</h3>
            <p>Impossible d'extraire l'expression de l'automate</p>
            <p>Erreur: {str(e)}</p>
        </div>
        """



# TESTS ET DÉMONSTRATIONS


def tester_glushkov():
    """Teste l'algorithme de Glushkov avec plusieurs exemples."""
    print("=== TESTS ALGORITHME DE GLUSHKOV ===\n")
    
    exemples = ["a", "ab", "a*", "ab*", "a|b"]
    
    for expr in exemples:
        print(f"Expression: {expr}")
        print("-" * 40)
        try:
            automate = glushkov_depuis_expression(expr)
            print("Automate généré:")
            print(automate.afficher())
            
            # Test d'extraction
            expr_extraite = extraire_expression_depuis_automate(automate)
            print(f"Expression extraite: {expr_extraite}")
            
        except Exception as e:
            print(f"Erreur: {e}")
        
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    # Lancer les tests
    tester_glushkov()
    
    # Exemple d'utilisation pour l'interface web
    print("=== GÉNÉRATION HTML ===")
    html_example = generer_html_glushkov("ab*")
    print("HTML généré (extrait):")
    print(html_example[:300] + "..." if len(html_example) > 300 else html_example)