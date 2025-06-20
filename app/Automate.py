from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any
from Etat import Etat
from Mot import Mot
from Langage import Langage
from collections import deque

class Automate(ABC):
    """Classe de base pour tous les automates"""
    
    def __init__(self, alphabet: Set[str], 
                 etats_finaux: Optional[Set[Etat]] = None,
                 etats: Optional[Set[Etat]] = None, 
                 etat_initial: Optional[Etat] = None) -> None:
        # Initialisation des structures de données
        self.alphabet = set(alphabet) if alphabet is not None else set()
        self.transitions = {}
        
        # Validation et initialisation des états
        if etats is None:
            raise ValueError("Un automate doit avoir des états")
        self.etats = etats
        
        # Validation et initialisation de l'état initial
        if etat_initial is None:
            raise ValueError("L'état initial doit être défini")
        if etat_initial not in self.etats:
            raise ValueError("L'état initial doit appartenir aux états")
        self.etat_initial = etat_initial
        self.etat_initial.est_initial = True
        
        # Gestion des états finaux (peuvent être vides)
        if etats_finaux is None:
            etats_finaux = set()
        
        # Vérification que les états finaux sont un sous-ensemble des états
        if not etats_finaux.issubset(self.etats):
            raise ValueError("Les états finaux doivent être un sous-ensemble des états")
        
        self.etats_finaux = etats_finaux
        for etat in self.etats_finaux:
            etat.est_final = True
    
    def ajouter_transition(self, source: Etat, symbole: str, destination: Etat):
        """Ajoute une transition à l'automate"""
        if source not in self.transitions:
            self.transitions[source] = {}
        if symbole not in self.transitions[source]:
            self.transitions[source][symbole] = set()
        self.transitions[source][symbole].add(destination)
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition de l'automate"""
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
            raise ValueError(f"Transition {etat_source}-{symbole}->{etat_cible} inexistante")
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        """Retourne les états accessibles par une transition"""
        if etat in self.transitions and symbole in self.transitions[etat]:
            return self.transitions[etat][symbole]
        return set()
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Détermine si un mot est reconnu par l'automate"""
        return self._reconnaitre_recursif(mot, self.etat_initial)

    def _reconnaitre_recursif(self, mot: str, etat_courant: Etat) -> bool:
        """Fonction récursive pour la reconnaissance de mots"""
        if not mot:
            # CORRECTION: 'etats_finaux' au lieu de 'etats_finals'
            return etat_courant in self.etats_finaux
        
        symbole = mot[0]
        reste = mot[1:]
        
        for etat_suivant in self.obtenir_transitions(etat_courant, symbole):
            if self._reconnaitre_recursif(reste, etat_suivant):
                return True
        return False
    
    def est_deterministe(self) -> bool:
        """Vérifie si l'automate est déterministe"""
        for etat in self.etats:
            if etat in self.transitions:
                for symbole in self.alphabet:
                    if symbole in self.transitions[etat]:
                        if len(self.transitions[etat][symbole]) > 1:
                            return False
        return True
    
    def est_complet(self) -> bool:
        """Vérifie si l'automate est complet"""
        for etat in self.etats:
            for symbole in self.alphabet:
                if not self.obtenir_transitions(etat, symbole):
                    return False
        return True
    
    def afficher(self) -> str:
        """Représentation textuelle de l'automate"""
        result = [
            f"Alphabet: {sorted(self.alphabet)}",
            f"États: {[str(e) for e in self.etats]}",
            f"État initial: {self.etat_initial}",
            f"États finaux: {[str(e) for e in self.etats_finaux]}",
            "Transitions:"
        ]
        
        for etat in sorted(self.transitions.keys(), key=str):
            for symbole in sorted(self.transitions[etat].keys()):
                for dest in sorted(self.transitions[etat][symbole], key=str):
                    result.append(f"  {etat} --{symbole}--> {dest}")
        
        return "\n".join(result)
    
    def automate_a_matrice(self) -> Tuple[List[List[Set[int]]], List[Etat], List[str]]:
        """Convertit l'automate en matrice de transitions"""
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


class ADC(Automate):
    """Automate Déterministe Complet"""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        
        if not self.est_deterministe():
            raise ValueError("L'automate n'est pas déterministe")
        if not self.est_complet():
            self.completer()
    
    def ajouter_transition(self, source: Etat, symbole: str, destination: Etat) -> None:
        if source in self.transitions and symbole in self.transitions[source]:
            raise ValueError(f"Transition déjà existante pour {source} --{symbole}->")
        super().ajouter_transition(source, symbole, destination)
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        destinations = super().obtenir_transitions(etat, symbole)
        if not destinations:
            return set()
        return destinations
    
    def reconnaitre_mot(self, mot: str) -> bool:
        etat_courant = self.etat_initial
        for symbole in mot:
            if symbole not in self.alphabet:
                return False
            next_states = self.obtenir_transitions(etat_courant, symbole)
            if not next_states:
                return False
            etat_courant = next(iter(next_states))
        return etat_courant in self.etats_finaux
    
    def est_deterministe(self) -> bool:
        return True
    
    def est_complet(self) -> bool:
        return True
    
    def completer(self) -> None:
        """Ajoute un état puits pour compléter l'automate"""
        puits = Etat("Puits")
        self.etats.add(puits)
        
        for etat in self.etats:
            for symbole in self.alphabet:
                if etat not in self.transitions or symbole not in self.transitions[etat]:
                    self.ajouter_transition(etat, symbole, puits)
    
    def afficher(self) -> str:
        return "[ADC] " + super().afficher()


class AFDC(ADC):
    """Automate Fini Déterministe Complet avec opérations avancées"""
    
    def minimiser(self) -> 'AFDC':
        """Algorithme de minimisation par partitionnement"""
        # Étape 1: Initialisation avec deux classes
        finaux = frozenset(self.etats_finaux)
        non_finaux = frozenset(self.etats - self.etats_finaux)
        
        # Ne garder que les classes non vides
        classes = set()
        if finaux:
            classes.add(finaux)
        if non_finaux:
            classes.add(non_finaux)
        
        # Créer une carte état -> classe
        classe_de = {}
        for etat in self.etats:
            if etat in self.etats_finaux:
                classe_de[etat] = finaux
            else:
                classe_de[etat] = non_finaux
        
        # Étape 2: Raffinage itératif
        while True:
            nouvelles_classes = set()
            groupes = {}
            
            for classe in classes:
                for etat in classe:
                    # Calculer la signature des transitions
                    signature = []
                    for symbole in self.alphabet:
                        if etat in self.transitions and symbole in self.transitions[etat]:
                            dest = next(iter(self.transitions[etat][symbole]))
                            signature.append(classe_de[dest])
                        else:
                            signature.append(None)
                    signature = tuple(signature)
                    
                    # Grouper par signature
                    if signature not in groupes:
                        groupes[signature] = set()
                    groupes[signature].add(etat)
            
            # Former les nouvelles classes
            nouvelles_classes = {frozenset(g) for g in groupes.values()}
            
            if nouvelles_classes == classes:
                break
            classes = nouvelles_classes
            
            # Mettre à jour la carte état->classe
            for classe in classes:
                for etat in classe:
                    classe_de[etat] = classe
        
        # Étape 3: Construction de l'automate minimal
        nouveaux_etats = {}
        for idx, classe in enumerate(classes):
            nom = f"Classe{idx}"
            nouvel_etat = Etat(nom)
            nouveaux_etats[classe] = nouvel_etat
        
        # Trouver état initial
        etat_initial_classe = next(c for c in classes if self.etat_initial in c)
        nouvel_initial = nouveaux_etats[etat_initial_classe]
        
        # Trouver états finaux
        nouveaux_finaux = {
            etat for classe, etat in nouveaux_etats.items()
            if classe & self.etats_finaux
        }
        
        # Créer le nouvel automate
        afdc_min = AFDC(
            self.alphabet,
            set(nouveaux_etats.values()),
            nouvel_initial,
            nouveaux_finaux
        )
        
        # Ajouter les transitions
        for classe, etat in nouveaux_etats.items():
            representant = next(iter(classe))
            for symbole in self.alphabet:
                if representant in self.transitions and symbole in self.transitions[representant]:
                    dest = next(iter(self.transitions[representant][symbole]))
                    dest_classe = next(c for c in classes if dest in c)
                    afdc_min.ajouter_transition(
                        etat,
                        symbole,
                        nouveaux_etats[dest_classe]
                    )
        
        return afdc_min
    
    def complementaire(self) -> 'AFDC':
        """Crée l'automate complémentaire"""
        nouveaux_finaux = self.etats - self.etats_finaux
        return AFDC(
            self.alphabet,
            self.etats,
            self.etat_initial,
            nouveaux_finaux
        )


class AND(Automate):
    """Automate Non Déterministe"""
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent"""
        # Initialisation avec l'état initial
        nouveaux_etats = {}
        file = deque()
        etat_initial_set = frozenset([self.etat_initial])
        file.append(etat_initial_set)
        nouveaux_etats[etat_initial_set] = Etat("q0")
        
        # Création des états de l'ADC
        while file:
            etat_set = file.popleft()
            
            for symbole in self.alphabet:
                # Calculer l'ensemble des états atteints
                nouvel_etat_set = set()
                for etat in etat_set:
                    if etat in self.transitions and symbole in self.transitions[etat]:
                        nouvel_etat_set.update(self.transitions[etat][symbole])
                
                if not nouvel_etat_set:
                    continue
                
                nouvel_etat_set = frozenset(nouvel_etat_set)
                
                if nouvel_etat_set not in nouveaux_etats:
                    nom = f"q{len(nouveaux_etats)}"
                    nouveaux_etats[nouvel_etat_set] = Etat(nom)
                    file.append(nouvel_etat_set)
        
        # Construction de l'ADC
        etats_adc = set(nouveaux_etats.values())
        etat_initial_adc = nouveaux_etats[etat_initial_set]
        etats_finaux_adc = {
            etat for etat_set, etat in nouveaux_etats.items()
            if any(e in self.etats_finaux for e in etat_set)
        }
        
        adc = ADC(self.alphabet, etats_adc, etat_initial_adc, etats_finaux_adc)
        
        # Ajout des transitions
        for etat_set, etat_obj in nouveaux_etats.items():
            for symbole in self.alphabet:
                nouvel_etat_set = set()
                for etat in etat_set:
                    if etat in self.transitions and symbole in self.transitions[etat]:
                        nouvel_etat_set.update(self.transitions[etat][symbole])
                
                if nouvel_etat_set:
                    nouvel_etat_set = frozenset(nouvel_etat_set)
                    if nouvel_etat_set in nouveaux_etats:
                        adc.ajouter_transition(
                            etat_obj,
                            symbole,
                            nouveaux_etats[nouvel_etat_set]
                        )
        
        return adc


class AFND(AND):
    """Automate Fini Non Déterministe"""
    
    def construction_sous_ensembles(self) -> AFDC:
        """Déterminisation avec retour typé AFDC"""
        return self.determiniser().minimiser()


class AFNS(AFND):
    """Automate avec ε-transitions"""
    
    def ajouter_transition_epsilon(self, source: Etat, destination: Etat) -> None:
        """Ajoute une ε-transition"""
        self.ajouter_transition(source, '', destination)
    
    def epsilon_fermeture(self, etat: Etat) -> Set[Etat]:
        """Calcule l'ε-fermeture d'un état"""
        fermeture = set()
        pile = [etat]
        
        while pile:
            courant = pile.pop()
            if courant not in fermeture:
                fermeture.add(courant)
                if courant in self.transitions and '' in self.transitions[courant]:
                    pile.extend(self.transitions[courant][''])
        
        return fermeture
    
    def epsilon_fermeture_ensemble(self, ensemble: Set[Etat]) -> Set[Etat]:
        """ε-fermeture pour un ensemble d'états"""
        return set.union(*(self.epsilon_fermeture(e) for e in ensemble)) if ensemble else set()
    
    def transiter(self, ensemble: Set[Etat], symbole: str) -> Set[Etat]:
        """Calcule les transitions depuis un ensemble d'états"""
        etapes = set()
        for etat in ensemble:
            if etat in self.transitions and symbole in self.transitions[etat]:
                etapes.update(self.transitions[etat][symbole])
        return self.epsilon_fermeture_ensemble(etapes)
    
    def eliminer_epsilon_transitions(self) -> AFND:
        """Élimine les ε-transitions pour obtenir un AFND équivalent"""
        # Calcul des nouvelles transitions
        nouvelles_transitions = {}
        
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            nouvelles_transitions[etat] = {}
            
            for symbole in self.alphabet - {''}:
                # Calcul des états atteints via symbole + ε-fermeture
                dests = self.epsilon_fermeture_ensemble(
                    self.transiter(fermeture, symbole)
                )
                if dests:
                    nouvelles_transitions[etat][symbole] = dests
        
        # Création du nouvel automate
        nouvel_initial = self.etat_initial
        
        # Gestion des états finaux
        nouveaux_finaux = {
            etat 
            for etat in self.etats
            if any(e in self.etats_finaux for e in self.epsilon_fermeture(etat))
        }
        
        # CORRECTION : Ordre des paramètres corrigé
        afnd = AFND(
            alphabet=self.alphabet,
            etats=self.etats,
            etat_initial=nouvel_initial,
            etats_finaux=nouveaux_finaux
        )
        
        # Ajout des nouvelles transitions
        for source, trans in nouvelles_transitions.items():
            for symbole, dests in trans.items():
                for dest in dests:
                    afnd.ajouter_transition(source, symbole, dest)
        
        return afnd
class AutomateCanonique(AFDC):
    """Automate minimal canonique selon Myhill-Nerode"""
    
    def __init__(self, langage: Langage) -> None:
        self.langage = langage
        self.construire_depuis_langage(langage)
    
    def relation_equivalence_droite(self, mot1: str, mot2: str) -> bool:
        """Vérifie si deux mots sont équivalents à droite"""
        # Pour tous les suffixes possibles
        for suffixe in self.langage.generer_suffixes():
            mot1_suff = Mot(mot1 + suffixe, self.langage.alphabet)
            mot2_suff = Mot(mot2 + suffixe, self.langage.alphabet)
            if (mot1_suff in self.langage) != (mot2_suff in self.langage):
                return False
        return True
    
    def classe_equivalence(self, mot: str) -> Set[str]:
        """Retourne la classe d'équivalence d'un mot"""
        return {m for m in self.langage.mots if self.relation_equivalence_droite(mot, m.contenu)}
    
    def construire_depuis_langage(self, langage: Langage) -> None:
        """Construit l'automate à partir des classes d'équivalence"""
        # Calcul des classes
        classes = {}
        for mot in langage.mots:
            classe = frozenset(self.classe_equivalence(mot.contenu))
            classes[classe] = classe
        
        # Création des états
        etats = {}
        for idx, classe in enumerate(classes):
            nom = f"C{idx}"
            etats[classe] = Etat(nom)
        
        # État initial (classe du mot vide)
        etat_initial = etats[self.classe_equivalence("")]
        
        # États finaux
        etats_finaux = {
            etat for classe, etat in etats.items() 
            if any(mot in langage for mot in classe)
        }
        
        # Initialisation de l'automate
        super().__init__(
            langage.alphabet,
            set(etats.values()),
            etat_initial,
            etats_finaux
        )
        
        # Ajout des transitions
        for classe, etat in etats.items():
            for symbole in langage.alphabet:
                # Prendre un mot représentatif
                mot_representatif = next(iter(classe))
                mot_dest = mot_representatif + symbole
                
                # Trouver la classe de destination
                classe_dest = next(c for c in classes if mot_dest in c)
                self.ajouter_transition(etat, symbole, etats[classe_dest])


# =============================================
# BLOC DE TEST
# =============================================

if __name__ == "__main__":
    def tester_automate_base():
        print("\n=== Test Automate de Base ===")
        
        # Création des états
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        
        # Création automate
        auto = Automate(
            alphabet={'a', 'b'},
            etats={q0, q1},
            etat_initial=q0,
            etats_finaux={q1}
        )
        
        # Ajout transitions
        auto.ajouter_transition(q0, 'a', q1)
        auto.ajouter_transition(q0, 'b', q0)
        auto.ajouter_transition(q1, 'a', q1)
        auto.ajouter_transition(q1, 'b', q0)
        
        # Tests
        print(auto.afficher())
        print(f"Déterministe: {auto.est_deterministe()}")
        print(f"Complet: {auto.est_complet()}")
        
        mots = ["a", "ba", "aba", "b"]
        for mot in mots:
            print(f"'{mot}' accepté? {auto.reconnaitre_mot(mot)}")
        
        # Test matrice
        matrice, etats, alpha = auto.automate_a_matrice()
        print("\nMatrice de transitions:")
        for i, etat in enumerate(etats):
            for j, symb in enumerate(alpha):
                print(f"{etat} -{symb}-> {[etats[k] for k in matrice[i][j]]}")

    def tester_adc():
        print("\n=== Test ADC ===")
        
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        puits = Etat("Puits")
        
        # Création ADC
        adc = ADC(
            alphabet={'a', 'b'},
            etats={q0, q1, puits},
            etat_initial=q0,
            etats_finaux={q1}
        )
        
        # Ajout transitions
        adc.ajouter_transition(q0, 'a', q1)
        adc.ajouter_transition(q0, 'b', puits)
        adc.ajouter_transition(q1, 'a', q1)
        adc.ajouter_transition(q1, 'b', puits)
        adc.ajouter_transition(puits, 'a', puits)
        adc.ajouter_transition(puits, 'b', puits)
        
        # Tests
        print(adc.afficher())
        print(f"Complet: {adc.est_complet()}")
        
        mots = ["a", "aa", "ab", "b", "ba"]
        for mot in mots:
            print(f"'{mot}' accepté? {adc.reconnaitre_mot(mot)}")
        
        # Test exception transition double
        try:
            adc.ajouter_transition(q0, 'a', puits)
            print("ERREUR: Double transition autorisée")
        except ValueError as e:
            print(f"Exception correcte: {e}")

    def tester_afdc():
        print("\n=== Test AFDC ===")
        
        # Création AFDC non minimal
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1", est_final=True)
        q2 = Etat("q2", est_final=True)
        
        afdc = AFDC(
            alphabet={'a', 'b'},
            etats={q0, q1, q2},
            etat_initial=q0,
            etats_finaux={q1, q2}
        )
        
        afdc.ajouter_transition(q0, 'a', q1)
        afdc.ajouter_transition(q0, 'b', q2)
        afdc.ajouter_transition(q1, 'a', q1)
        afdc.ajouter_transition(q1, 'b', q1)
        afdc.ajouter_transition(q2, 'a', q2)
        afdc.ajouter_transition(q2, 'b', q2)
        
        print("=== Avant minimisation ===")
        print(afdc.afficher())
        
        # Minimisation
        afdc_min = afdc.minimiser()
        print("\n=== Après minimisation ===")
        print(afdc_min.afficher())
        
        # Complémentation
        afdc_comp = afdc_min.complementaire()
        print("\n=== Complémentaire ===")
        print(afdc_comp.afficher())
        
        # Test reconnaissance
        mots = ["a", "b", "aa", "bb"]
        print("\nReconnaissance:")
        for mot in mots:
            print(f"'{mot}': original={afdc_min.reconnaitre_mot(mot)}, complément={afdc_comp.reconnaitre_mot(mot)}")

    def tester_and():
        print("\n=== Test AND ===")
        
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1")
        q2 = Etat("q2", est_final=True)
        
        and_auto = AND(
            alphabet={'a', 'b'},
            etats={q0, q1, q2},
            etat_initial=q0,
            etats_finaux={q2}
        )
        
        # Transitions non déterministes
        and_auto.ajouter_transition(q0, 'a', q1)
        and_auto.ajouter_transition(q0, 'a', q2)
        and_auto.ajouter_transition(q1, 'b', q2)
        
        print(and_auto.afficher())
        print(f"Déterministe: {and_auto.est_deterministe()}")
        
        # Test reconnaissance
        mots = ["a", "ab", "b", "aa"]
        for mot in mots:
            print(f"'{mot}' accepté? {and_auto.reconnaitre_mot(mot)}")
        
        # Déterminisation
        adc_det = and_auto.determiniser()
        print("\n=== Après déterminisation ===")
        print(adc_det.afficher())

    def tester_afns():
        print("\n=== Test AFNS ===")
        
        q0 = Etat("q0", est_initial=True)
        q1 = Etat("q1")
        q2 = Etat("q2", est_final=True)
        
        afns = AFNS(
            alphabet={'a', 'b'},
            etats={q0, q1, q2},
            etat_initial=q0,
            etats_finaux={q2}
        )
        
        # Transitions avec epsilon
        afns.ajouter_transition_epsilon(q0, q1)
        afns.ajouter_transition(q1, 'a', q2)
        afns.ajouter_transition(q0, 'b', q2)
        
        print("=== AFNS original ===")
        print(afns.afficher())
        
        # Test epsilon-fermeture
        print("\nε-fermeture de q0:", [str(e) for e in afns.epsilon_fermeture(q0)])
        
        # Test reconnaissance
        print(f"'a' accepté? {afns.reconnaitre_mot('a')}")
        print(f"'b' accepté? {afns.reconnaitre_mot('b')}")
        print(f"'' accepté? {afns.reconnaitre_mot('')}")
        
        # Élimination des ε-transitions
        afnd = afns.eliminer_epsilon_transitions()
        print("\n=== Après élimination des ε-transitions ===")
        print(afnd.afficher())

    
    # Exécution des tests
    tester_automate_base()
    tester_adc()
    tester_afdc()
    tester_and()
    tester_afns()