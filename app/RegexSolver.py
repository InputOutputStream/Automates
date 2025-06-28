import re
from collections import deque

class RegexSystemSolver:
    def __init__(self):
        self.system = {}
        self.solutions = {}
        self.order = []
        self.variables = set()
        self.dependencies = {}  # Stocke les dépendances de chaque variable
        
    def add_equation(self, var, expr):
        """Ajoute une équation au système"""
        self.system[var] = expr
        self.order.append(var)
        self.variables.add(var)
        
        # Extraction des dépendances
        self.dependencies[var] = self._extract_variables(expr)
        
    def _extract_variables(self, expr):
        """Extrait les variables d'une expression"""
        # Utilise une regex pour trouver les noms de variables (majuscules suivies de chiffres)
        return set(re.findall(r'[A-Z][0-9]*', expr))
    
    def compute_elimination_order(self):
        """Calcule l'ordre d'élimination optimal avec tri topologique"""
        # Construire le graphe de dépendances
        graph = {}
        reverse_graph = {var: set() for var in self.variables}
        in_degree = {}
        
        for var in self.variables:
            # Les dépendances externes (exclut la variable elle-même)
            deps = self.dependencies[var] - {var}
            graph[var] = deps
            in_degree[var] = len(deps)
            
            # Construire le graphe inverse
            for dep in deps:
                if dep in reverse_graph:
                    reverse_graph[dep].add(var)
        
        # Tri topologique
        queue = deque()
        for var in self.variables:
            if in_degree[var] == 0:
                queue.append(var)
                
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            
            # Mettre à jour les dépendances des voisins
            for neighbor in reverse_graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Gestion des cycles (variables restantes)
        remaining = [var for var in self.variables if var not in order]
        if remaining:
            # Trier par complexité d'équation (plus courtes d'abord)
            remaining.sort(key=lambda var: len(self.system[var]))
            order.extend(remaining)
        
        return order
    
    def solve_system(self, elimination_order=None):
        """Résout le système selon l'ordre d'élimination spécifié"""
        if elimination_order is None:
            elimination_order = self.compute_elimination_order()
        
        # Copie temporaire du système
        temp_system = self.system.copy()
        
        for var in elimination_order:
            if var not in temp_system:
                continue
                
            # Étape 1: Résolution partielle de la variable
            expr = temp_system[var]
            
            # Séparation des termes contenant la variable et des autres
            terms = [t.strip() for t in expr.split('+')]
            self_terms = []
            other_terms = []
            
            for term in terms:
                if term == var:  # Cas: X
                    self_terms.append("")
                elif term.endswith(var):  # Cas: aX
                    prefix = term[:-len(var)]
                    self_terms.append(prefix)
                else:
                    other_terms.append(term)
            
            # Construction de A et R
            A = self._format_union(self_terms)
            R = self._format_union(other_terms)
            
            # Calcul de A*R
            if A == "∅":
                solution = "∅"
            elif A == "ε":
                solution = R
            else:
                A_star = self._format_star(A)
                solution = self._format_concat(A_star, R)
            
            # Stockage de la solution
            self.solutions[var] = solution
            del temp_system[var]
            
            # Étape 2: Substitution dans les autres équations
            for other_var in temp_system:
                expr = temp_system[other_var]
                new_terms = []
                
                for term in expr.split('+'):
                    term = term.strip()
                    if term == var:  # Cas: X
                        new_terms.append(f"({solution})")
                    elif term.endswith(var):  # Cas: aX
                        prefix = term[:-len(var)]
                        new_term = self._format_concat(prefix, solution)
                        new_terms.append(new_term)
                    else:
                        new_terms.append(term)
                
                temp_system[other_var] = '+'.join(new_terms)
        
        return self.solutions
    
    def find_shortest_resolved(self):
        """Trouve la solution complètement résolue la plus courte"""
        # Vérifie quelles solutions ne contiennent plus de variables
        resolved = []
        for var, expr in self.solutions.items():
            if not self._contains_variables(expr):
                resolved.append((var, expr))
        
        if not resolved:
            return None, "Aucune solution complètement résolue"
        
        # Trie par longueur d'expression
        resolved.sort(key=lambda x: len(x[1]))
        return resolved[0]
    
    def _contains_variables(self, expr):
        """Vérifie si l'expression contient des variables"""
        # Détecte les noms de variables dans l'expression
        for var in self.variables:
            if var in expr:
                return True
        return False
    
    def _format_union(self, terms):
        """Formate une union de termes"""
        if not terms:
            return "∅"
        
        # Filtre des termes vides
        filtered = []
        for term in terms:
            if term == "":
                filtered.append("ε")
            elif term == "∅":
                continue
            else:
                filtered.append(term)
        
        if not filtered:
            return "∅"
        if len(filtered) == 1:
            return filtered[0]
        return '(' + '+'.join(filtered) + ')'
    
    def _format_star(self, expr):
        """Applique l'opération étoile"""
        if expr == "∅":
            return "∅"
        if expr == "ε":
            return "ε"
        if '+' in expr or '*' in expr:
            return '(' + expr + ')*'
        return expr + '*'
    
    def _format_concat(self, a, b):
        """Formate une concaténation"""
        if a == "∅" or b == "∅":
            return "∅"
        if a == "ε":
            return b
        if b == "ε":
            return a
        
        # Ajout de parenthèses si nécessaire
        a_paren = '(' + a + ')' if '+' in a else a
        b_paren = '(' + b + ')' if '+' in b else b
        
        return a_paren + b_paren

    def display_solutions(self):
        """Affiche les solutions"""
        print("\n=== Solutions finales ===")
        for var in self.order:
            print(f"{var} = {self.solutions.get(var, '?')}")

if __name__ == "__main__":
    solver = RegexSystemSolver()
    
    # Définition du système d'équations
    solver.add_equation("A", "bA + aB")
    solver.add_equation("B", "aD + bC")
    solver.add_equation("D", "aB + bC + ε")
    solver.add_equation("C", "bB + aC")
    
    # Calcul de l'ordre d'élimination optimal
    order = solver.compute_elimination_order()
    print(f"Ordre d'élimination optimal: {order}")
    
    # Résolution dans l'ordre optimal
    solutions = solver.solve_system(elimination_order=order)
    
    # Affichage des résultats
    solver.display_solutions()
    
    # Recherche de la solution complètement résolue la plus courte
    var, expr = solver.find_shortest_resolved()
    print(f"\nSolution complètement résolue la plus courte: {var} = {expr}")