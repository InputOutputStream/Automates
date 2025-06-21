from typing import Set, Dict, List, Tuple, Optional, Union, Any
from Mot import Mot
from .Langage import Langage
from .Automate import Automate, ADC, AFDC, AND, AFND, AFNS, AutomateCanonique
from .Etat import Etat
from collections import deque


class LangageReconnaissable(Langage):
    """
    Langage reconnaissable (régulier).
    Implémente les propriétés de clôture des langages reconnaissables.
    """

    def __init__(self, mots: Optional[Set[Mot]] = None, alphabet: Optional[Set[str]] = None,
                 automate: Optional[Automate] = None) -> None:
        """Initialise un langage reconnaissable."""
        super().__init__(mots=mots, alphabet=alphabet)
        self.automate = automate
        if automate is not None:
            self.alphabet = automate.alphabet
            # Update mots based on the automate, if provided
            self.mots = self._generate_mots_from_automate(longueur_max=100)  # Arbitrary limit for generation
        elif mots is not None and alphabet is not None:
            # Construct a canonical automaton for the language if none provided
            self.automate = AutomateCanonique(self)

    def _generate_mots_from_automate(self, longueur_max: int) -> Set[Mot]:
        """Generate words accepted by the automaton up to a maximum length."""
        if self.automate is None:
            return set()
        mots = set()
        def explore(etat: Etat, mot_courant: str, longueur: int):
            if longueur > longueur_max:
                return
            if etat.est_final:
                mots.add(Mot(mot_courant))
            if etat in self.automate.transitions:
                for symbole in self.automate.transitions[etat]:
                    for dest in self.automate.transitions[etat][symbole]:
                        explore(dest, mot_courant + symbole, longueur + 1)
        explore(self.automate.etat_initial, "", 0)
        return mots

    def complementation(self) -> 'LangageReconnaissable':
        """Clôture par complémentation."""
        if self.automate is None:
            raise ValueError("Aucun automate défini pour le langage")
        # Ensure the automaton is deterministic and complete (AFDC)
        if not isinstance(self.automate, AFDC):
            self.automate = AFND(self.automate.alphabet, self.automate.etats,
                                 self.automate.etat_initial, self.automate.etats_finaux).construction_sous_ensembles()
        # Compute the complement
        automate_comp = self.automate.complementaire()
        return LangageReconnaissable(automate=automate_comp)

    def union_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par union ensembliste."""
        if self.automate is None or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate défini")
        
        # Convert both automata to AFND if necessary
        aut1 = self.automate if isinstance(self.automate, AFND) else AFND(
            self.automate.alphabet, self.automate.etats, self.automate.etat_initial, self.automate.etats_finaux)
        aut2 = autre.automate if isinstance(autre.automate, AFND) else AFND(
            autre.automate.alphabet, autre.automate.etats, autre.automate.etat_initial, autre.automate.etats_finaux)
        
        # Create a new alphabet (union of both)
        alphabet = aut1.alphabet | aut2.alphabet
        
        # Create a new initial state
        new_initial = Etat("q_initial", est_initial=True)
        new_etats = aut1.etats | aut2.etats | {new_initial}
        
        # Create new final states (union of final states)
        new_finals = aut1.etats_finaux | aut2.etats_finaux
        
        # Create new automaton
        new_automate = AFND(alphabet, new_etats, new_initial, new_finals)
        
        # Copy transitions from both automata
        new_automate.transitions = aut1.transitions.copy()
        for etat, trans in aut2.transitions.items():
            new_automate.transitions[etat] = trans.copy()
        
        # Add epsilon transitions from new initial state
        new_automate.ajouter_transition_epsilon(new_initial, aut1.etat_initial)
        new_automate.ajouter_transition_epsilon(new_initial, aut2.etat_initial)
        
        # Determinize to AFDC
        result_automate = new_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=result_automate)

    def intersection_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par intersection ensembliste."""
        if self.automate is None or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate défini")
        
        # Ensure both automata are AFDC
        aut1 = self.automate if isinstance(self.automate, AFDC) else AFND(
            self.automate.alphabet, self.automate.etats, self.automate.etat_initial, self.automate.etats_finaux).construction_sous_ensembles()
        aut2 = autre.automate if isinstance(autre.automate, AFDC) else AFND(
            autre.automate.alphabet, autre.automate.etats, autre.automate.etat_initial, autre.automate.etats_finaux).construction_sous_ensembles()
        
        # Create product automaton
        alphabet = aut1.alphabet | aut2.alphabet
        new_etats = set()
        new_finals = set()
        etat_mapping = {}
        
        # Create states as pairs (q1, q2)
        for q1 in aut1.etats:
            for q2 in aut2.etats:
                new_etat = Etat(f"({q1.nom},{q2.nom})")
                new_etats.add(new_etat)
                etat_mapping[(q1, q2)] = new_etat
                if q1 in aut1.etats_finaux and q2 in aut2.etats_finaux:
                    new_etat.est_final = True
                    new_finals.add(new_etat)
        
        # Initial state
        new_initial = etat_mapping[(aut1.etat_initial, aut2.etat_initial)]
        new_initial.est_initial = True
        
        # Create product automaton
        product_automate = AFDC(alphabet, new_etats, new_initial, new_finals)
        
        # Add transitions
        for (q1, q2), new_etat in etat_mapping.items():
            for symbole in alphabet:
                next1 = aut1.obtenir_transitions(q1, symbole)
                next2 = aut2.obtenir_transitions(q2, symbole)
                if next1 and next2:
                    dest1 = next(iter(next1))
                    dest2 = next(iter(next2))
                    product_automate.ajouter_transition(new_etat, symbole, etat_mapping[(dest1, dest2)])
        
        return LangageReconnaissable(automate=product_automate)

    def miroir(self) -> 'LangageReconnaissable':
        """Clôture par miroir."""
        if self.automate is None:
            raise ValueError("Aucun automate défini pour le langage")
        
        # Create a new automaton for the mirror language
        new_etats = self.automate.etats.copy()
        new_alphabet = self.automate.alphabet.copy()
        new_initial = Etat("q_miroir_initial", est_initial=True)
        new_finals = {self.automate.etat_initial}  # Original initial state becomes final
        new_etats.add(new_initial)
        
        new_automate = AFND(new_alphabet, new_etats, new_initial, new_finals)
        
        # Reverse transitions
        for etat_source, transitions in self.automate.transitions.items():
            for symbole, destinations in transitions.items():
                for dest in destinations:
                    new_automate.ajouter_transition(dest, symbole, etat_source)
        
        # Connect new initial state to original final states
        for final_state in self.automate.etats_finaux:
            new_automate.ajouter_transition_epsilon(new_initial, final_state)
        
        # Determinize to AFDC
        result_automate = new_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=result_automate)

    def concatenation(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par concaténation."""
        if self.automate is None or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate défini")
        
        # Convert to AFND
        aut1 = self.automate if isinstance(self.automate, AFND) else AFND(
            self.automate.alphabet, self.automate.etats, self.automate.etat_initial, self.automate.etats_finaux)
        aut2 = autre.automate if isinstance(autre.automate, AFND) else AFND(
            autre.automate.alphabet, autre.automate.etats, autre.automate.etat_initial, autre.automate.etats_finaux)
        
        # Create new automaton
        alphabet = aut1.alphabet | aut2.alphabet
        new_etats = aut1.etats | aut2.etats
        new_initial = aut1.etat_initial
        new_finals = aut2.etats_finaux
        
        new_automate = AFND(alphabet, new_etats, new_initial, new_finals)
        
        # Copy transitions
        new_automate.transitions = aut1.transitions.copy()
        for etat, trans in aut2.transitions.items():
            new_automate.transitions[etat] = trans.copy()
        
        # Connect final states of first automaton to initial state of second
        for final_state in aut1.etats_finaux:
            new_automate.ajouter_transition_epsilon(final_state, aut2.etat_initial)
        
        # Determinize to AFDC
        result_automate = new_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=result_automate)

    def etoile(self, longueur_max: int) -> 'LangageReconnaissable':
        """Clôture par étoile (étoile de Kleene)."""
        if longueur_max < 0:
            raise ValueError("Longueur maximale doit être non négative")
        if self.automate is None:
            raise ValueError("Aucun automate défini pour le langage")
        
        # Convert to AFND
        aut = self.automate if isinstance(self.automate, AFND) else AFND(
            self.automate.alphabet, self.automate.etats, self.automate.etat_initial, self.automate.etats_finaux)
        
        # Create new automaton
        new_initial = Etat("q_etoile_initial", est_initial=True)
        new_etats = aut.etats | {new_initial}
        new_finals = aut.etats_finaux | {new_initial}
        
        new_automate = AFND(aut.alphabet, new_etats, new_initial, new_finals)
        
        # Copy original transitions
        new_automate.transitions = aut.transitions.copy()
        
        # Add epsilon transitions
        new_automate.ajouter_transition_epsilon(new_initial, aut.etat_initial)
        for final_state in aut.etats_finaux:
            new_automate.ajouter_transition_epsilon(final_state, aut.etat_initial)
        
        # Generate words up to longueur_max
        result_automate = new_automate.construction_sous_ensembles()
        return LangageReconnaissable(automate=result_automate)

    def regex_vers_langage(self, expression_reguliere: str) -> None:
        """Construit le langage depuis une expression régulière."""
        # Simplified implementation (would require a full regex parser in practice)
        # For demonstration, assume simple regex like "a*b" or "(a|b)"
        if not expression_reguliere:
            self.mots = set()
            self.alphabet = set()
            self.automate = None
            return
        
        # Example: Parse simple regex like "a*b"
        alphabet = set(expression_reguliere.replace("*", "").replace("|", "").replace("(", "").replace(")", ""))
        etats = {Etat(f"q{i}") for i in range(3)}  # Simplified state set
        initial = Etat("q0", est_initial=True)
        final = Etat("q2", est_final=True)
        
        aut = AFND(alphabet, etats, initial, {final})
        
        # Example for "a*b"
        if expression_reguliere == "a*b":
            aut.ajouter_transition(initial, "a", initial)
            aut.ajouter_transition(initial, "b", final)
        # Add more regex parsing logic as needed
        
        self.automate = aut.construction_sous_ensembles()
        self.alphabet = alphabet
        self.mots = self._generate_mots_from_automate(100)

    def langage_vers_regex(self) -> str:
        """Convertit le langage en expression régulière."""
        if self.automate is None:
            return ""
        
        # Use state elimination or similar algorithm (simplified here)
        # For demonstration, return a placeholder regex
        return "L"  # Replace with actual state elimination algorithm

    def theoreme_kleene_construction(self, automate: Automate) -> str:
        """Application du théorème de Kleene pour la construction."""
        # Convert automaton to regex using state elimination
        if not isinstance(automate, AFDC):
            automate = AFND(automate.alphabet, automate.etats, automate.etat_initial, automate.etats_finaux).construction_sous_ensembles()
        
        # Placeholder: Implement state elimination algorithm
        return "L"  # Replace with actual regex construction

    def lemme_pompage_verification(self, mot: Mot) -> Tuple[bool, Dict[str, Any]]:
        """Vérifie le lemme de pompage pour un mot."""
        if self.automate is None:
            raise ValueError("Aucun automate défini pour le langage")
        
        # Ensure AFDC
        aut = self.automate if isinstance(self.automate, AFDC) else AFND(
            self.automate.alphabet, self.automate.etats, self.automate.etat_initial, self.automate.etats_finaux).construction_sous_ensembles()
        
        p = len(aut.etats)  # Pumping length
        mot_str = str(mot)
        
        if len(mot_str) < p:
            return True, {"message": "Mot trop court pour le lemme de pompage"}
        
        # Try to find a decomposition uvw with |uv| <= p and |v| > 0
        for i in range(1, p + 1):
            for j in range(1, p - i + 1):
                u = mot_str[:i]
                v = mot_str[i:i+j]
                w = mot_str[i+j:]
                if not v:
                    continue
                
                # Check if uv^kw is in the language for all k >= 0
                all_pumped = True
                for k in range(3):  # Test a few iterations
                    pumped_word = u + v * k + w
                    if not aut.reconnaitre_mot(pumped_word):
                        all_pumped = False
                        break
                
                if all_pumped:
                    return True, {"u": u, "v": v, "w": w, "p": p}
        
        return False, {"message": "Le mot ne satisfait pas le lemme de pompage"}

    def lemme_pompage_application(self) -> bool:
        """Application du lemme de pompage au langage."""
        if self.automate is None:
            return True  # Empty language is regular
        
        # Check if the language is regular by testing a few long words
        for mot in self.mots:
            if len(str(mot)) >= len(self.automate.etats):
                result, _ = self.lemme_pompage_verification(mot)
                if not result:
                    return False
        return True

    def lemme_darden(self) -> bool:
        """Application du lemme d'Arden."""
        # Arden's lemma: If L = A + BL, then L = B*A
        # Simplified check: Verify if the language can be expressed as a regular expression
        return self.langage_vers_regex() != ""  # Placeholder

    def resolution_partielle_gauss(self, systeme_equations: List[str]) -> Dict[str, 'Langage']:
        """Résolution partielle par méthode de Gauss."""
        # Assume equations are of the form Xi = Ai + sum(Bij * Xj)
        result = {}
        for eq in systeme_equations:
            # Parse equation (simplified)
            var, expr = eq.split("=")
            var = var.strip()
            # Construct language from expression (placeholder)
            result[var] = LangageReconnaissable()
        return result

    def substitution_gauss(self, variable: str, expression: 'Langage') -> 'Langage':
        """Substitution dans un système d'équations."""
        # Substitute variable with expression in the language
        return expression  # Placeholder