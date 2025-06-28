import re
from typing import Set, Dict, List, Tuple, Optional, Union, Any
from collections import deque

from .Mot import Mot
from .Langage import Langage
from .Automate import Automate, ADC, AFDC, AND, AFND, AFNS, AutomateMinimal
from .Etat import Etat
from .RegexSolver import RegexSystemSolver


class AlphabetError(Exception):
    """Exception levée lors d'erreurs d'alphabet."""
    pass


class LangageReconnaissable(Langage):
    """
    Langage reconnaissable (régulier).
    Implémente les propriétés de clôture des langages reconnaissables.
    """

    def __init__(self, mots: Optional[Set[Mot]] = None, 
                 alphabet: Optional[Set[str]] = None,
                 automate: Optional[Automate] = None) -> None:
        """Initialise un langage reconnaissable."""
        super().__init__(mots=mots, alphabet=alphabet)
        self.automate = automate
        
        if automate is not None:
            self.alphabet = automate.alphabet
            self.mots = self._generer_mots_depuis_automate(longueur_max=100)
        elif mots is not None and alphabet is not None:
            self.automate = AutomateMinimal(self)

    def _generer_mots_depuis_automate(self, longueur_max: int) -> Set[Mot]:
        if self.automate is None:
            return set()

        mots = set()
        # Initialiser avec l'état initial et le mot vide
        q = deque([(self.automate.etat_initial, Mot("", self.automate.alphabet))])
        # Visited pour éviter les cycles et la redondance, peut être (etat, mot_tuple)
        # Ou simplement (etat, longueur_mot) pour éviter la génération infinie
        visited = {(self.automate.etat_initial, "")} 

        while q:
            current_state, current_word = q.popleft()

            if current_state.est_final:
                mots.add(current_word)

            if len(current_word.value) >= longueur_max: # Limite la longueur
                continue

            # Assurez-vous que current_state est dans les clés de transitions
            if current_state in self.automate.transitions:
                # Itérer sur les symboles et leurs destinations
                for symbol, destinations in self.automate.transitions[current_state].items():
                    for next_state in destinations:
                        next_word_value = current_word.value + symbol
                        next_word = Mot(next_word_value, self.automate.alphabet)

                        if (next_state, next_word_value) not in visited:
                            visited.add((next_state, next_word_value))
                            q.append((next_state, next_word))

            # Gérer les epsilon transitions si l'automate les supporte
            if hasattr(self.automate, 'epsilon') and self.automate.epsilon in self.automate.transitions.get(current_state, {}):
                for next_state_epsilon in self.automate.transitions[current_state][self.automate.epsilon]:
                    if (next_state_epsilon, current_word.value) not in visited: # Mot reste le même
                        visited.add((next_state_epsilon, current_word.value))
                        q.append((next_state_epsilon, current_word))
        return mots
    
    def _verifier_automate_defini(self) -> None:
        """Vérifie qu'un automate est défini pour le langage."""
        if self.automate is None:
            raise ValueError("Aucun automate défini pour le langage")

    def _verifier_deux_automates_definis(self, autre: 'LangageReconnaissable') -> None:
        """Vérifie que les deux langages ont un automate défini."""
        if self.automate is None or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate défini")

    def _convertir_vers_afdc(self, automate: Automate) -> AFDC:
        """Convertit un automate vers AFDC si nécessaire."""
        if isinstance(automate, AFDC):
            return automate
        
        afnd = AFND(automate.alphabet, automate.etats,
                   automate.etat_initial, automate.etats_finaux)
        return afnd.construction_sous_ensembles()

    def _convertir_vers_afnd(self, automate: Automate) -> AFND:
        """Convertit un automate vers AFND si nécessaire."""
        if isinstance(automate, AFND):
            return automate
        
        return AFND(automate.alphabet, automate.etats,
                   automate.etat_initial, automate.etats_finaux)

    # ==================== PROPRIÉTÉS DE CLÔTURE ====================

    def complementation(self) -> 'LangageReconnaissable':
        """Clôture par complémentation."""
        self._verifier_automate_defini()
        
        afdc = self._convertir_vers_afdc(self.automate)
        automate_comp = afdc.complementaire()
        
        return LangageReconnaissable(automate=automate_comp)

    def union_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par union ensembliste."""
        self._verifier_deux_automates_definis(autre)
        
        aut1 = self._convertir_vers_afnd(self.automate)
        aut2 = self._convertir_vers_afnd(autre.automate)
        
        # Créer nouvel alphabet (union des deux)
        alphabet = aut1.alphabet | aut2.alphabet
        
        # Créer nouvel état initial
        nouveau_initial = Etat("q_initial", est_initial=True)
        nouveaux_etats = aut1.etats | aut2.etats | {nouveau_initial}
        nouveaux_finals = aut1.etats_finaux | aut2.etats_finaux
        
        # Créer nouvel automate
        nouvel_automate = AFND(alphabet, nouveaux_etats, nouveau_initial, nouveaux_finals)
        
        # Copier les transitions des deux automates
        nouvel_automate.transitions = aut1.transitions.copy()
        for etat, trans in aut2.transitions.items():
            nouvel_automate.transitions[etat] = trans.copy()
        
        # Ajouter transitions epsilon depuis le nouvel état initial
        nouvel_automate.ajouter_transition_epsilon(nouveau_initial, aut1.etat_initial)
        nouvel_automate.ajouter_transition_epsilon(nouveau_initial, aut2.etat_initial)
        
        # Déterminiser vers AFDC
        resultat_automate = nouvel_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=resultat_automate)

    def intersection_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par intersection ensembliste."""
        self._verifier_deux_automates_definis(autre)
        
        aut1 = self._convertir_vers_afdc(self.automate)
        aut2 = self._convertir_vers_afdc(autre.automate)
        
        # Créer automate produit
        alphabet = aut1.alphabet | aut2.alphabet
        nouveaux_etats = set()
        nouveaux_finals = set()
        mapping_etats = {}
        
        # Créer états comme paires (q1, q2)
        for q1 in aut1.etats:
            for q2 in aut2.etats:
                nouvel_etat = Etat(f"({q1.nom},{q2.nom})")
                nouveaux_etats.add(nouvel_etat)
                mapping_etats[(q1, q2)] = nouvel_etat
                
                if q1 in aut1.etats_finaux and q2 in aut2.etats_finaux:
                    nouvel_etat.est_final = True
                    nouveaux_finals.add(nouvel_etat)
        
        # État initial
        nouveau_initial = mapping_etats[(aut1.etat_initial, aut2.etat_initial)]
        nouveau_initial.est_initial = True
        
        # Créer automate produit
        automate_produit = AFDC(alphabet, nouveaux_etats, nouveau_initial, nouveaux_finals)
        
        # Ajouter transitions
        for (q1, q2), nouvel_etat in mapping_etats.items():
            for symbole in alphabet:
                next1 = aut1.obtenir_transitions(q1, symbole)
                next2 = aut2.obtenir_transitions(q2, symbole)
                
                if next1 and next2:
                    dest1 = next(iter(next1))
                    dest2 = next(iter(next2))
                    automate_produit.ajouter_transition(
                        nouvel_etat, symbole, mapping_etats[(dest1, dest2)]
                    )
        
        return LangageReconnaissable(automate=automate_produit)

    def miroir(self) -> 'LangageReconnaissable':
        """Clôture par miroir."""
        self._verifier_automate_defini()
        
        nouveaux_etats = self.automate.etats.copy()
        nouvel_alphabet = self.automate.alphabet.copy()
        nouveau_initial = Etat("q_miroir_initial", est_initial=True)
        nouveaux_finals = {self.automate.etat_initial}
        nouveaux_etats.add(nouveau_initial)
        
        nouvel_automate = AFND(nouvel_alphabet, nouveaux_etats, nouveau_initial, nouveaux_finals)
        
        # Inverser les transitions
        for etat_source, transitions in self.automate.transitions.items():
            for symbole, destinations in transitions.items():
                for dest in destinations:
                    nouvel_automate.ajouter_transition(dest, symbole, etat_source)
        
        # Connecter nouvel état initial aux anciens états finaux
        for etat_final in self.automate.etats_finaux:
            nouvel_automate.ajouter_transition_epsilon(nouveau_initial, etat_final)
        
        resultat_automate = nouvel_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=resultat_automate)

    def concatenation(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par concaténation."""
        self._verifier_deux_automates_definis(autre)
        
        aut1 = self._convertir_vers_afnd(self.automate)
        aut2 = self._convertir_vers_afnd(autre.automate)
        
        alphabet = aut1.alphabet | aut2.alphabet
        nouveaux_etats = aut1.etats | aut2.etats
        nouveau_initial = aut1.etat_initial
        nouveaux_finals = aut2.etats_finaux
        
        nouvel_automate = AFND(alphabet, nouveaux_etats, nouveau_initial, nouveaux_finals)
        
        # Copier transitions
        nouvel_automate.transitions = aut1.transitions.copy()
        for etat, trans in aut2.transitions.items():
            nouvel_automate.transitions[etat] = trans.copy()
        
        # Connecter états finaux du premier aux états initiaux du second
        for etat_final in aut1.etats_finaux:
            nouvel_automate.ajouter_transition_epsilon(etat_final, aut2.etat_initial)
        
        resultat_automate = nouvel_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=resultat_automate)

    def etoile(self) -> 'LangageReconnaissable':
        """Clôture par étoile (étoile de Kleene)."""
        self._verifier_automate_defini()
        
        aut = self._convertir_vers_afnd(self.automate)
        
        nouveau_initial = Etat("q_etoile_initial", est_initial=True)
        nouveaux_etats = aut.etats | {nouveau_initial}
        nouveaux_finals = aut.etats_finaux | {nouveau_initial}
        
        nouvel_automate = AFND(aut.alphabet, nouveaux_etats, nouveau_initial, nouveaux_finals)
        
        # Copier transitions originales
        nouvel_automate.transitions = aut.transitions.copy()
        
        # Ajouter transitions epsilon
        nouvel_automate.ajouter_transition_epsilon(nouveau_initial, aut.etat_initial)
        for etat_final in aut.etats_finaux:
            nouvel_automate.ajouter_transition_epsilon(etat_final, aut.etat_initial)
        
        resultat_automate = nouvel_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=resultat_automate)

    # ==================== CONVERSION REGEX ====================

    def regex_vers_langage(self, expression_reguliere: str) -> None:
        """Construit le langage depuis une expression régulière."""
        if not expression_reguliere:
            self.mots = set()
            self.alphabet = set()
            self.automate = None
            return
        
        # Implémentation simplifiée (nécessiterait un parseur regex complet)
        alphabet = set(expression_reguliere.replace("*", "").replace("|", "")
                      .replace("(", "").replace(")", ""))
        etats = {Etat(f"q{i}") for i in range(3)}
        initial = Etat("q0", est_initial=True)
        final = Etat("q2", est_final=True)
        
        aut = AFND(alphabet, etats, initial, {final})
        
        # Exemple pour "a*b"
        if expression_reguliere == "a*b":
            aut.ajouter_transition(initial, "a", initial)
            aut.ajouter_transition(initial, "b", final)
        
        self.automate = aut.construction_sous_ensembles()
        self.alphabet = alphabet
        self.mots = self._generer_mots_depuis_automate(100)

    def langage_vers_regex(self) -> str:
        """Convertit le langage en expression régulière."""
        self._verifier_automate_defini()
        
        # Utiliser la construction de Thompson inversée ou élimination d'états
        return self._theoreme_kleene_construction(self.automate)

    def _theoreme_kleene_construction(self, automate: Automate) -> str:
        """Convertit un automate en expression régulière via élimination d'états."""
        afdc = self._convertir_vers_afdc(automate)
        
        # Créer un système d'équations
        systeme = {}
        for etat in afdc.etats:
            expr = []
            if etat.est_initial:
                expr.append('e')  # Epsilon pour l'état initial
            for symbole, destinations in afdc.transitions.get(etat, {}).items():
                for dest in destinations:
                    expr.append(f"{symbole}{dest.nom}")
            systeme[etat.nom] = '+'.join(expr) if expr else '∅'
        
        # Résoudre avec le lemme d'Arden
        variables = {etat.nom for etat in afdc.etats}
        solutions = self.appliquer_lemmes_arden(systeme, afdc.alphabet, variables)
        
        # Récupérer l'expression pour les états finaux
        final_expr = []
        for etat in afdc.etats_finaux:
            if etat.nom in solutions:
                final_expr.append(solutions[etat.nom])
        
        return '+'.join(final_expr) if final_expr else '∅'

# ==================== UTILITAIRES POUR LEMMES D'ARDEN ====================

    @staticmethod
    def appliquer_lemmes_arden(systeme: Dict[str, str],):
        solver = RegexSystemSolver()
        for eqn in systeme:
            var, exp = eqn.strip(" ").split("=")
            print(var, "=", exp)
            solver.add_equation(var, exp)
    
        order = solver.compute_elimination_order()
        solutions = solver.solve_system(elimination_order=order)
        print(solutions)
        var, expr = solver.find_shortest_resolved()
        return expr

   # =================== Automate vers Regex ==========================
    @classmethod
    def arden_dfa_to_regex(cls, automaton):
        states = automaton["states"]
        transitions = automaton["transitions"]
        initial = automaton["initial_state"]
        finals = set(automaton["final_states"])
        
        # Initialisation des équations
        equations = {}
        for state in states:
            equations[state] = {
                'to': {},
                'const': 'ε' if state in finals else '∅'
            }
        
        # Remplir les transitions
        for t in transitions:
            src = t['source']
            sym = t['symbol']
            dst = t['destination']
            if dst in equations[src]['to']:
                old_expr = equations[src]['to'][dst]
                equations[src]['to'][dst] = cls._create_union(old_expr, sym)
            else:
                equations[src]['to'][dst] = sym

        # États à éliminer (sauf l'état initial)
        states_to_eliminate = [s for s in states if s != initial]
        
        for k in states_to_eliminate:
            # Résoudre l'équation pour l'état k
            expr_kk = equations[k]['to'].get(k, '∅')
            other_terms = {j: expr for j, expr in equations[k]['to'].items() if j != k}
            const_k = equations[k]['const']
            
            # Application du lemme d'Arden : R = A*B où A est la boucle, B le reste
            if expr_kk == '∅':
                # Pas de boucle : Rk = const_k + Σ(transitions vers autres états)
                Rk_expr = {'to': other_terms, 'const': const_k}
            else:
                # Il y a une boucle : Rk = A*(B + const_k)
                # où A = expr_kk, B = autres transitions
                
                # Appliquer A* aux autres termes
                new_terms = {}
                for j, expr in other_terms.items():
                    # A* . expr
                    concat_result = cls._create_concatenation(f"({expr_kk})*", expr)
                    new_terms[j] = concat_result
                
                # Appliquer A* à la constante
                if const_k == '∅':
                    new_const = '∅'
                else:
                    # A* . const_k
                    new_const = cls._create_concatenation(f"({expr_kk})*", const_k)
                
                Rk_expr = {'to': new_terms, 'const': new_const}
            
            # Substituer Rk dans les autres équations
            for i in states:
                if i == k or i not in equations:
                    continue
                if k not in equations[i]['to']:
                    continue
                    
                expr_ik = equations[i]['to'][k]
                del equations[i]['to'][k]  # Supprimer le terme contenant k
                
                # Ajouter les contributions de Rk_expr
                for j, expr_kj in Rk_expr['to'].items():
                    # expr_ik . expr_kj
                    new_expr = cls._create_concatenation(expr_ik, expr_kj)
                    if j in equations[i]['to']:
                        old_expr = equations[i]['to'][j]
                        equations[i]['to'][j] = cls._create_union(old_expr, new_expr)
                    else:
                        equations[i]['to'][j] = new_expr
                
                # Traiter le terme constant
                if Rk_expr['const'] != '∅':
                    new_const_term = cls._create_concatenation(expr_ik, Rk_expr['const'])
                    if equations[i]['const'] == '∅':
                        equations[i]['const'] = new_const_term
                    else:
                        equations[i]['const'] = cls._create_union(equations[i]['const'], new_const_term)
            
            # Supprimer l'état k des équations
            del equations[k]
        
        # Résoudre l'équation finale pour l'état initial
        if initial in equations[initial]['to']:
            loop_expr = equations[initial]['to'][initial]
        else:
            loop_expr = '∅'
        const_expr = equations[initial]['const']
        
        # Application finale du lemme d'Arden
        if loop_expr == '∅':
            result = const_expr
        else:
            # R = A*B où A = loop_expr, B = const_expr
            if const_expr == '∅':
                result = '∅'
            else:
                result = cls._create_concatenation(f"({loop_expr})*", const_expr)
        
        return cls.simplify_regex(result)

    @classmethod
    def _create_union(cls, expr1, expr2):
        """Crée une union en gérant les cas particuliers"""
        if expr1 == '∅':
            return expr2
        if expr2 == '∅':
            return expr1
        if expr1 == expr2:  # Idempotence
            return expr1
        return f"({expr1}+{expr2})"

    @classmethod
    def _create_concatenation(cls, expr1, expr2):
        """Crée une concaténation en gérant les cas particuliers"""
        if expr1 == '∅' or expr2 == '∅':
            return '∅'
        if expr1 == 'ε':
            return expr2
        if expr2 == 'ε':
            return expr1
        return f"{expr1}{expr2}"

    @classmethod
    def simplify_regex(cls, expr):
        """Simplifie une expression régulière selon les propriétés algébriques"""
        if not expr or expr == '':
            return 'ε'
        
        # Cas de base
        if expr == '∅':
            return '∅'
        if expr == 'ε':
            return 'ε'
        
        # Appliquer les simplifications de manière itérative
        prev_expr = None
        current_expr = expr
        
        while prev_expr != current_expr:
            prev_expr = current_expr
            current_expr = cls._apply_simplification_rules(current_expr)
        
        return current_expr

    @classmethod
    def _apply_simplification_rules(cls, expr):
        """Applique une passe de simplification"""
        
        # 1. Neutralité de ε dans la concaténation
        expr = re.sub(r'ε([a-zA-Z0-9(])', r'\1', expr)  # ε.X -> X
        expr = re.sub(r'([a-zA-Z0-9)])ε', r'\1', expr)  # X.ε -> X
        expr = expr.replace('ε', '')  # Supprimer les ε isolés
        
        # 2. Élément absorbant ∅ dans la concaténation
        expr = re.sub(r'∅[^+)]*', '∅', expr)  # ∅.X -> ∅
        expr = re.sub(r'[^+(]*∅', '∅', expr)  # X.∅ -> ∅
        
        # 3. Neutralité de ∅ dans l'union
        expr = re.sub(r'\(∅\+([^)]+)\)', r'\1', expr)  # (∅+X) -> X
        expr = re.sub(r'\(([^)]+)\+∅\)', r'\1', expr)  # (X+∅) -> X
        expr = re.sub(r'^∅\+', '', expr)  # ∅+X -> X (début)
        expr = re.sub(r'\+∅$', '', expr)  # X+∅ -> X (fin)
        expr = re.sub(r'\+∅\+', '+', expr)  # X+∅+Y -> X+Y
        
        # 4. Idempotence de l'union : X+X -> X
        expr = re.sub(r'\(([^)]+)\+\1\)', r'\1', expr)
        
        # 5. Propriétés des itérations
        expr = re.sub(r'∅\*', 'ε', expr)  # ∅* -> ε
        expr = re.sub(r'ε\*', 'ε', expr)  # ε* -> ε
        expr = re.sub(r'\(([^)]*)\*\)\*', r'(\1)*', expr)  # (X*)* -> X*
        
        # 6. Simplifications avec L*L = L+ (représenté comme LL*)
        expr = re.sub(r'([a-zA-Z0-9]+)\*\1', r'\1\1*', expr)  # X*X -> XX* (= X+)
        expr = re.sub(r'([a-zA-Z0-9]+)\1\*', r'\1\1*', expr)  # XX* -> XX* (déjà simplifié)
        
        # 7. Distributivité : factorisation
        # A(B+C) déjà géré par la construction
        # (B+C)A -> BA+CA pourrait être ajouté si nécessaire
        
        # 8. Nettoyer les parenthèses inutiles
        expr = re.sub(r'\(([^+()]*)\)', r'\1', expr)  # (X) -> X si pas d'union
        
        # 9. Nettoyer les expressions vides
        expr = expr.replace('()', '')
        expr = expr.strip('+')
        
        # 10. Gérer les cas où il ne reste rien
        if not expr or expr == '':
            return 'ε'
            
        return expr

  


    def lemme_pompage_verification(self, mot: Mot) -> Tuple[bool, Dict[str, Any]]:
        """Vérifie le lemme de pompage pour un mot."""
        self._verifier_automate_defini()
        
        aut = self._convertir_vers_afdc(self.automate)
        p = len(aut.etats)  # Longueur de pompage
        mot_str = str(mot)
        
        if len(mot_str) < p:
            return True, {"message": "Mot trop court pour le lemme de pompage"}
        
        # Essayer de trouver une décomposition uvw avec |uv| <= p et |v| > 0
        for i in range(1, p + 1):
            for j in range(1, p - i + 1):
                u = mot_str[:i]
                v = mot_str[i:i+j]
                w = mot_str[i+j:]
                
                if not v:
                    continue
                
                # Vérifier si uv^kw est dans le langage pour tout k >= 0
                tout_pompe = True
                for k in range(3):  # Tester quelques itérations
                    mot_pompe = u + v * k + w
                    if not aut.reconnaitre_mot(mot_pompe):
                        tout_pompe = False
                        break
                
                if tout_pompe:
                    return True, {"u": u, "v": v, "w": w, "p": p}
        
        return False, {"message": "Le mot ne satisfait pas le lemme de pompage"}

    def lemme_pompage_application(self) -> bool:
        """Application du lemme de pompage au langage."""
        if self.automate is None:
            return True  # Langage vide est régulier
        
        # Vérifier si le langage est régulier en testant quelques mots longs
        for mot in self.mots:
            if len(str(mot)) >= len(self.automate.etats):
                resultat, _ = self.lemme_pompage_verification(mot)
                if not resultat:
                    return False
        return True

    def lemme_darden(self) -> bool:
        """Application du lemme d'Arden."""
        # Lemme d'Arden : Si L = A + BL, alors L = B*A
        # Vérification simplifiée : le langage peut-il être exprimé comme regex
        try:
            return bool(self.langage_vers_regex())
        except:
            return False

    # ==================== MÉTHODES DE RÉSOLUTION ====================

    def resolution_partielle_gauss(self, systeme_equations: List[str]) -> Dict[str, 'LangageReconnaissable']:
        """Résolution partielle par méthode de Gauss."""
        # Assume equations are of the form Xi = Ai + sum(Bij * Xj)
        resultat = {}
        for eq in systeme_equations:
            # Parse equation (simplified)
            if "=" in eq:
                var, expr = eq.split("=", 1)
                var = var.strip()
                # Construire langage depuis expression (placeholder)
                resultat[var] = LangageReconnaissable()
        return resultat

    def substitution_gauss(self, variable: str, expression: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Substitution dans un système d'équations."""
        # Substituer variable par expression dans le langage
        return expression  # Placeholder

    def __str__(self) -> str:
        """Représentation string du langage."""
        if self.mots:
            mots_str = ", ".join(str(mot) for mot in sorted(self.mots, key=str))
            return f"LangageReconnaissable({{{mots_str}}})"
        elif self.automate:
            return f"LangageReconnaissable(automate={type(self.automate).__name__})"
        else:
            return "LangageReconnaissable(vide)"

    def __repr__(self) -> str:
        """Représentation pour débogage."""
        return self.__str__()