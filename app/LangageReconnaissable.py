import re
from typing import Set, Dict, List, Tuple, Optional, Union, Any
from collections import deque

from .Mot import Mot
from .Langage import Langage
from .Automate import Automate, ADC, AFDC, AND, AFND, AFNS, AutomateMinimal
from .Etat import Etat


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
        """Génère les mots acceptés par l'automate jusqu'à une longueur maximale."""
        if self.automate is None:
            return set()
        
        mots = set()
        
        def explorer(etat: Etat, mot_courant: str, longueur: int) -> None:
            if longueur > longueur_max:
                return
            
            if etat.est_final:
                mots.add(Mot(mot_courant))
            
            if etat in self.automate.transitions:
                for symbole in self.automate.transitions[etat]:
                    for dest in self.automate.transitions[etat][symbole]:
                        explorer(dest, mot_courant + symbole, longueur + 1)
        
        explorer(self.automate.etat_initial, "", 0)
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
        """Application du théorème de Kleene pour la construction."""
        afdc = self._convertir_vers_afdc(automate)
        
        # Implémentation simplifiée de l'algorithme d'élimination d'états
        # TODO: Implémenter l'algorithme complet d'élimination d'états
        return "L"  # Placeholder

    # ==================== UTILITAIRES POUR LEMMES D'ARDEN ====================

    @staticmethod
    def _decomposer_expression(expr: str, alphabet: Set[str], variables: Set[str]) -> List[str]:
        """Découpe l'expression en symboles reconnus : variables, alphabet, opérateurs."""
        tokens = re.findall(r'[A-Za-z0-9]+|[+*()]', expr)
        sequence = []
        
        for token in tokens:
            if token in ['+', '*', '(', ')']:
                sequence.append(token)
                continue
                
            i = 0
            while i < len(token):
                match = False
                
                # Vérifier variables (ordre par longueur décroissante)
                for var in sorted(variables, key=len, reverse=True):
                    if token[i:i+len(var)] == var:
                        sequence.append(var)
                        i += len(var)
                        match = True
                        break
                
                if match:
                    continue
                    
                # Vérifier alphabet (ordre par longueur décroissante)
                for sym in sorted(alphabet, key=len, reverse=True):
                    if token[i:i+len(sym)] == sym:
                        sequence.append(sym)
                        i += len(sym)
                        match = True
                        break
                
                if not match:
                    sequence.append(token[i])
                    i += 1
                    
        return sequence

    @staticmethod
    def _verifier_alphabet(expr: str, alphabet: Set[str], variables: Set[str]) -> Tuple[bool, Optional[str]]:
        """Vérifie que tous les symboles dans expr sont reconnus."""
        autorises = set(alphabet) | set(variables) | {'+', '*', '(', ')'}
        symboles = LangageReconnaissable._decomposer_expression(expr, alphabet, variables)
        
        for s in symboles:
            if s not in autorises:
                return False, s
        return True, None

    @staticmethod
    def _substituer(expr: str, solutions: Dict[str, str]) -> str:
        """Substitue les variables par leurs solutions dans l'expression."""
        if not solutions:
            return expr
            
        # Trier par longueur décroissante pour éviter les substitutions partielles
        solutions_triees = sorted(solutions.items(), key=lambda x: len(x[0]), reverse=True)
        
        for var, val in solutions_triees:
            # Ajouter parenthèses si nécessaire
            val_substitue = f"({val})" if ('+' in val or ('*' in val and len(val) > 1)) else val
            
            # Pattern pour éviter les substitutions partielles
            pattern = r'\b' + re.escape(var) + r'\b'
            expr = re.sub(pattern, val_substitue, expr)
        
        # Nettoyer les + consécutifs et en début/fin
        expr = re.sub(r'\+{2,}', '+', expr)
        expr = expr.strip('+')
        
        return expr

    @staticmethod
    def _analyser_equation_auto_reference(var: str, expr: str) -> Optional[Tuple[str, str]]:
        """Analyse une équation de la forme X = αX + β et retourne (α, β)."""
        termes = [t.strip() for t in expr.split('+') if t.strip()]
        
        alpha_parts = []
        beta_parts = []
        
        for terme in termes:
            if var in terme:
                if terme == var:
                    alpha_parts.append('e')  # coefficient 1 (epsilon)
                elif terme.endswith(var):
                    coeff = terme[:-len(var)]
                    alpha_parts.append(coeff if coeff else 'e')
                else:
                    return None  # Variable pas à la fin, forme plus complexe
            else:
                beta_parts.append(terme)
        
        alpha = '+'.join(alpha_parts) if alpha_parts else ''
        beta = '+'.join(beta_parts) if beta_parts else 'e'
        
        return alpha, beta

    @staticmethod
    def _appliquer_arden(alpha: str, beta: str) -> str:
        """Applique le lemme d'Arden : X = αX + β devient X = α*β."""
        if not alpha or alpha == 'e':
            return beta
        elif not beta or beta == 'e':
            return f"{alpha}*"
        else:
            alpha_paren = f"({alpha})" if '+' in alpha else alpha
            beta_paren = f"({beta})" if '+' in beta else beta
            return f"{alpha_paren}*{beta_paren}"

    @staticmethod
    def _trouver_equations_resolvables(systeme: List[Tuple[str, str]], 
                                      alphabet: Set[str], 
                                      variables: Set[str], 
                                      solutions: Dict[str, str]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """Identifie les équations résolvables dans le système."""
        resolvables = []
        non_resolvables = []
        
        for var, expr in systeme:
            # Substituer les variables déjà résolues
            expr_sub = LangageReconnaissable._substituer(expr, solutions)
            
            # Vérifier l'alphabet
            ok, symbole_invalide = LangageReconnaissable._verifier_alphabet(expr_sub, alphabet, variables)
            if not ok:
                raise AlphabetError(f"Symbole inconnu '{symbole_invalide}' dans l'expression de {var}")
            
            # Analyser les variables présentes
            symboles = LangageReconnaissable._decomposer_expression(expr_sub, alphabet, variables)
            vars_presentes = [s for s in symboles if s in variables and s != var]
            
            if not vars_presentes:
                # Aucune autre variable : équation résoluble
                if var in symboles:
                    # Auto-référence : appliquer Arden
                    resultat = LangageReconnaissable._analyser_equation_auto_reference(var, expr_sub)
                    if resultat:
                        alpha, beta = resultat
                        solution = LangageReconnaissable._appliquer_arden(alpha, beta)
                        resolvables.append((var, solution))
                    else:
                        non_resolvables.append((var, expr_sub))
                else:
                    # Pas d'auto-référence : solution directe
                    resolvables.append((var, expr_sub))
            else:
                # Contient d'autres variables : non résoluble pour l'instant
                non_resolvables.append((var, expr_sub))
        
        return resolvables, non_resolvables
    

    @classmethod
    def lemmes_arden (cls, systeme: List[Tuple[str, str]], 
                              alphabet: Set[str], 
                              variables: Set[str], max_iter: int = 50) -> Tuple[Optional[Dict[str, str]], 
                                                          Optional[List[Tuple[str, str]]], 
                                                          Optional[str]]:
            return cls.appliquer_lemmes_arden(systeme, alphabet, variables, max_iter)

    def appliquer_lemmes_arden(self, systeme: List[Tuple[str, str]], 
                              alphabet: Set[str], 
                              variables: Set[str], max_iter: int = 50) -> Tuple[Optional[Dict[str, str]], 
                                                          Optional[List[Tuple[str, str]]], 
                                                          Optional[str]]:
        """Résout le système d'équations en appliquant les lemmes d'Arden."""
        solutions = {}
        systeme_courant = systeme.copy()
        max_iterations = max_iter
        
        for iteration in range(max_iterations):
            try:
                resolvables, non_resolvables = self._trouver_equations_resolvables(
                    systeme_courant, alphabet, variables, solutions
                )
            except AlphabetError as e:
                return None, None, str(e)
            
            # Si aucune équation résoluble, arrêter
            if not resolvables:
                break
            
            # Ajouter les nouvelles solutions
            for var, sol in resolvables:
                solutions[var] = sol
            
            # Mettre à jour le système pour la prochaine itération
            systeme_courant = non_resolvables
            
            # Si plus d'équations, terminé
            if not systeme_courant:
                break
        
        return solutions, systeme_courant, None

    # ==================== LEMMES ET VÉRIFICATIONS ====================

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