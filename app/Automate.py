from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any
from Etat import Etat
from Mot import Mot
from Langage import Langage


class Automate(ABC):
    """
    Classe représentant un automate selon la définition du cours.
    
    - alphabet: ensemble de symboles
    - etats: ensemble d'états
    - etat_initial: état de départ
    - etats_finaux: ensemble d'états finaux
    - fonction_transition: fonction de transition
    """
    
    def __init__(self, alphabet: Set[str], 
                 etats_finaux: Optional[Set[Etat]] = None,
                 etats: Optional[Set[Etat]] = None, 
                 etat_initial : Optional[Etat] = None) -> None:
        """
        Initialise l'automate avec ses composants de base.
        
        Args:
            alphabet: Ensemble des symboles de l'alphabet
            etats: Ensemble des états
            etat_initial: État initial
            etats_finaux: Ensemble des états finaux
        """
        self.alphabet = set(alphabet) if alphabet is not None else set()
        self.transitions = {}

        if etats is not None:
            self.etats = etats  
        else :
            raise ValueError("Un automate doit avoir des etats")
        
        if etat_initial is not None and etat_initial in self.etats:
            self.etat_initial = etat_initial  
            self.etat_initial.est_initial = True
        else :
            raise ValueError("L'état initial doit être défini et appartenir aux états")
        
        if etats_finaux is not None and etats_finaux & self.etats :
            self.etats_finaux = etats_finaux  
            for etat in self.etats_finaux:
                etat.est_final = True
        else :
            raise ValueError("Un automate doit avoir des états finaux")
        
    def ajouter_transition(self, source: Etat, symbole: str, destination: Etat):
        """Ajoute une transition à l'automate."""
        if source not in self.transitions:
            self.transitions[source] = {}
        if symbole not in self.transitions[source]:
            self.transitions[source][symbole] = set()
        self.transitions[source][symbole].add(destination)

    def matrice_a_automate(self, matrice: list[list]):
        pass

    def automate_a_matrice(self):
        """Conversion temporaire pour algorithmes matriciels"""
        etats_list = list(self.etats)
        alphabet_list = list(self.alphabet)
        n = len(etats_list)
        m = len(alphabet_list)
        
        matrice = [[set() for _ in range(m)] for _ in range(n)]
        
        for i, etat in enumerate(etats_list):
            if etat in self.transitions:
                for j, symbole in enumerate(alphabet_list):
                    if symbole in self.transitions[etat]:
                        for dest in self.transitions[etat][symbole]:
                            k = etats_list.index(dest)
                            matrice[i][j].add(k)
        
        return matrice, etats_list, alphabet_list
    
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition de l'automate."""
        if (etat_source in self.transitions and 
            symbole in self.transitions[etat_source] and
            etat_cible in self.transitions[etat_source][symbole]):
            
            self.transitions[etat_source][symbole].remove(etat_cible)
            
            # Nettoyer les structures vides
            if not self.transitions[etat_source][symbole]:
                del self.transitions[etat_source][symbole]
            if not self.transitions[etat_source]:
                del self.transitions[etat_source]
        else:
            raise IndexError("etat_source, etat_cible ou transisions inconnu")
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne l'ensemble des états accessibles depuis un état avec un symbole."""
        if etat in self.transitions and symbole in self.transitions[etat]:
            return self.transitions[etat][symbole]
        return set()    
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Détermine si un mot est reconnu par l'automate."""
        return self._reconnaitre_recursif(mot, self.etat_initial)

    def _reconnaitre_recursif(self, mot: str, etat_courant: Etat):
        """Fonction récursive pour la reconnaissance de mots."""

        if not mot:
            return etat_courant.est_final
    
        symbole = mot[0]
        reste_du_mot = mot[1:]

        etats_suivants = self.obtenir_transitions(etat_courant, symbole)

        for etat_suivant in etats_suivants:
            if self._reconnaitre_recursif(reste_du_mot, etat_suivant):
                return True
                
        return False
    
    def est_deterministe(self) -> bool:
        """Vérifie si l'automate est déterministe."""
        """
            En princippe ici "" est notre epsilon, mais on va voir comment il se comporte 
            avec les testes
        """
        for etat in self.etats:
            if etat in self.transitions:
                for symbole in self.alphabet:
                    if symbole in self.transitions[etat]:
                        if len(self.transitions[etat][symbole]) > 1:
                            return False
        return True
       
    def est_complet(self) -> bool:
        """Vérifie si l'automate est complet."""
        for etat in self.etats:
            for symbole in self.alphabet:
                if not self.obtenir_transitions(etat, symbole):
                    return False
        return True
    
    def afficher(self) -> str:
        """Retourne une représentation textuelle de l'automate."""
        result = []
        result.append(f"Alphabet: {sorted(self.alphabet)}")
        result.append(f"États: {[str(e) for e in self.etats]}")
        result.append(f"État initial: {self.etat_initial}")
        result.append(f"États finaux: {[str(e) for e in self.etats_finaux]}")
        result.append("Transitions:")
        
        for etat_source in sorted(self.transitions.keys(), key=str):
            for symbole in sorted(self.transitions[etat_source].keys()):
                destinations = self.transitions[etat_source][symbole]
                for dest in sorted(destinations, key=str):
                    result.append(f"  {etat_source} --{symbole}--> {dest}")
        
        return "\n".join(result)
    




class ADC(Automate):
    """
    Automate Déterministe Complet.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux ADC (déterminisme et complétude).
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un ADC."""
        pass
    
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition en respectant le déterminisme."""
        pass
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition en maintenant la complétude."""
        pass
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne exactement un état (déterminisme)."""
        pass
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance déterministe d'un mot."""
        pass
    
    def est_deterministe(self) -> bool:
        """Retourne toujours True pour un ADC."""
        pass
    
    def est_complet(self) -> bool:
        """Retourne toujours True pour un ADC."""
        pass
    
    def completer(self) -> None:
        """Complète l'automate s'il ne l'est pas déjà."""
        pass
    
    def afficher(self) -> str:
        """Affichage spécifique aux ADC."""
        pass


class AFDC(ADC):
    """
    Automate Fini Déterministe Complet.
    
    Surcharge des méthodes d'ADC pour les propriétés spécifiques aux AFDC.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFDC."""
        pass
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        pass
    
    def minimiser(self) -> 'AFDC':
        """Retourne l'automate minimal équivalent."""
        pass
    
    def complementaire(self) -> 'AFDC':
        """Retourne l'automate complémentaire."""
        pass


class AND(Automate):
    """
    Automate Non Déterministe.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux automates non déterministes.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AND."""
        pass
    
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition non déterministe."""
        pass
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition non déterministe."""
        pass
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne un ensemble d'états (non déterminisme)."""
        pass
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance non déterministe d'un mot."""
        pass
    
    def est_deterministe(self) -> bool:
        """Vérifie le déterminisme."""
        pass
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        pass
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        pass
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        pass


class AFND(AND):
    """
    Automate Fini Non Déterministe.
    
    Composants:
    - alphabet: Σ ensemble fini de symboles
    - etats: Q ensemble fini d'états  
    - etat_initial: état initial
    - etats_finaux: F ⊂ Q états finaux
    - fonction_transition: δ ⊂ Q × Σ × Q relation de transition
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFND."""
        pass
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        pass
    
    def construction_sous_ensembles(self) -> AFDC:
        """Algorithme de construction des sous-ensembles pour déterminiser."""
        pass


class AFNS(AFND):
    """
    Automate Fini à Transitions Spontanées (ε-transitions).
    
    Composants:
    - alphabet: Σ ensemble fini de symboles
    - etats: Q ensemble fini d'états
    - etat_initial: I ∈ Q état initial
    - etats_finaux: F ⊂ Q états finaux
    - fonction_transition: δ ⊂ Q × (Σ ∪ {ε}) × Q relation de transition
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFNS."""
        pass
    
    def ajouter_transition_epsilon(self, etat_source: str, etat_cible: str) -> None:
        """Ajoute une ε-transition."""
        pass
    
    def supprimer_transition_epsilon(self, etat_source: str, etat_cible: str) -> None:
        """Supprime une ε-transition."""
        pass
    
    def epsilon_fermeture(self, etat: str) -> Set[str]:
        """Calcule l'ε-fermeture d'un état."""
        pass
    
    def epsilon_fermeture_ensemble(self, ensemble_etats: Set[str]) -> Set[str]:
        """Calcule l'ε-fermeture d'un ensemble d'états."""
        pass
    
    def transiter(self, ensemble_etats: Set[str], symbole: str) -> Set[str]:
        """Calcule les transitions depuis un ensemble d'états avec un symbole."""
        pass
    
    def construction_sous_ensembles(self) -> AFDC:
        """
        Construction des sous-ensembles.
        Entrée: Un AFNS
        Sortie: Un AFDC équivalent
        """
        pass
    
    def eliminer_epsilon_transitions(self) -> AFND:
        """Élimine les ε-transitions pour obtenir un AFND équivalent."""
        pass


class AutomateCanonique(AFDC):
    """
    Automate canonique selon le théorème de Myhill-Nerode.
    
    Implémente les concepts de:
    - Théorème 15 (De Myhill-Nerode)
    - Théorème 16 (Automate canonique)
    - Minimisation
    """
    
    def __init__(self, langage: 'Langage') -> None:
        """Construit l'automate canonique d'un langage."""
        pass
    
    def relation_equivalence_droite(self, mot1: str, mot2: str) -> bool:
        """Vérifie si deux mots sont équivalents à droite."""
        pass
    
    def classe_equivalence(self, mot: str) -> Set[str]:
        """Retourne la classe d'équivalence d'un mot."""
        pass
    
    def nombre_classes_equivalence(self) -> int:
        """Retourne le nombre de classes d'équivalence."""
        pass
    
    def construire_depuis_langage(self, langage: 'Langage') -> None:
        """Construit l'automate canonique depuis un langage."""
        pass
    
    def est_minimal(self) -> bool:
        """Vérifie si l'automate est minimal."""
        pass







# =============================================
# DÉMONSTRATION D'UTILISATION
# =============================================

if __name__ == "__main__":
    print("=== DÉMONSTRATION DE LA CLASSE AUTOMATE ===\n")
    
    # Création des états
    q0 = Etat("q0", est_initial=True)
    q1 = Etat("q1", est_final=True) 
    q2 = Etat("q2")
    
    # Exemple 1: Automate simple qui accepte les mots finissant par 'a'
    print("1. Automate acceptant les mots finissant par 'a'")
    automate1 = Automate(
        alphabet={'a', 'b'},
        etats={q0, q1},
        etat_initial=q0,
        etats_finaux={q1}
    )
    
    # Ajout des transitions
    automate1.ajouter_transition(q0, 'a', q1)  # q0 --a--> q1
    automate1.ajouter_transition(q0, 'b', q0)  # q0 --b--> q0  
    automate1.ajouter_transition(q1, 'a', q1)  # q1 --a--> q1
    automate1.ajouter_transition(q1, 'b', q0)  # q1 --b--> q0
    
    print(automate1.afficher())
    print(f"Déterministe: {automate1.est_deterministe()}")
    print(f"Complet: {automate1.est_complet()}")
    
    # Test de reconnaissance
    mots_test = ["a", "ba", "bba", "ab", "bb", ""]
    for mot in mots_test:
        resultat = automate1.reconnaitre_mot(mot)
        print(f"Mot '{mot}': {'✓' if resultat else '✗'}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 2: Automate non-déterministe
    print("2. Automate non-déterministe (deux transitions pour 'a' depuis q0)")
    automate2 = Automate(
        alphabet={'a', 'b'},
        etats={q0, q1, q2},
        etat_initial=q0,
        etats_finaux={q2}
    )
    
    # Transitions non-déterministes
    automate2.ajouter_transition(q0, 'a', q1)  # q0 --a--> q1
    automate2.ajouter_transition(q0, 'a', q2)  # q0 --a--> q2 (non-déterministe!)
    automate2.ajouter_transition(q1, 'b', q2)  # q1 --b--> q2
    
    print(automate2.afficher())
    print(f"Déterministe: {automate2.est_deterministe()}")
    print(f"Complet: {automate2.est_complet()}")
    
    # Test de reconnaissance
    mots_test2 = ["a", "ab", "b", "aa"]
    for mot in mots_test2:
        resultat = automate2.reconnaitre_mot(mot)
        print(f"Mot '{mot}': {'✓' if resultat else '✗'}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 3: Conversion en matrice
    print("3. Conversion automate → matrice")
    matrice, etats_list, alphabet_list = automate1.automate_a_matrice()
    
    print(f"États: {[str(e) for e in etats_list]}")
    print(f"Alphabet: {alphabet_list}")
    print("Matrice de transitions:")
    for i, etat in enumerate(etats_list):
        for j, symbole in enumerate(alphabet_list):
            destinations = matrice[i][j]
            if destinations:
                dest_noms = [str(etats_list[k]) for k in destinations]
                print(f"  {etat} --{symbole}--> {dest_noms}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 4: Manipulation des transitions
    print("4. Suppression de transitions")
    print("Avant suppression:")
    print(automate1.afficher())
    
    # Supprimer une transition
    automate1.supprimer_transition(q1, 'b', q0)
    print("\nAprès suppression de q1 --b--> q0:")
    print(automate1.afficher())
    print(f"Complet après suppression: {automate1.est_complet()}")