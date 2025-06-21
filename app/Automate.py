from abc import ABC
from typing import Set, Dict, List, Optional
from .Etat import Etat
from .Langage import Langage
from collections import deque


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
    """Automate Déterministe Complet."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        """Initialise un ADC."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_deterministe():
            raise ValueError("L'automate doit être déterministe")
        self.completer()
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Ajoute une transition en respectant le déterminisme."""
        if etat_source in self.transitions and symbole in self.transitions[etat_source]:
            if self.transitions[etat_source][symbole]:
                raise ValueError("Transition déjà définie - violation du déterminisme")
        super().ajouter_transition(etat_source, symbole, etat_cible)
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition en maintenant la complétude."""
        super().supprimer_transition(etat_source, symbole, etat_cible)
        self.completer()  # Maintenir la complétude
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        """Retourne exactement un état (déterminisme)."""
        transitions = super().obtenir_transitions(etat, symbole)
        return transitions  # Sera toujours de taille 0 ou 1 pour un ADC
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance déterministe d'un mot."""
        etat_courant = self.etat_initial
        for symbole in mot:
            transitions = self.obtenir_transitions(etat_courant, symbole)
            if not transitions:
                return False
            etat_courant = next(iter(transitions))  # Un seul état possible
        return etat_courant.est_final
    
    def est_deterministe(self) -> bool:
        """Retourne toujours True pour un ADC."""
        return True
    
    def est_complet(self) -> bool:
        """Retourne toujours True pour un ADC."""
        return True
    
    def completer(self) -> None:
        """Complète l'automate s'il ne l'est pas déjà."""
        if super().est_complet():
            return
        
        # Créer un état puits si nécessaire
        etat_puits = Etat("puits")
        self.etats.add(etat_puits)
        
        # Ajouter les transitions manquantes vers l'état puits
        for etat in self.etats:
            for symbole in self.alphabet:
                if not super().obtenir_transitions(etat, symbole):
                    self.ajouter_transition(etat, symbole, etat_puits)
        
        # L'état puits boucle sur lui-même
        for symbole in self.alphabet:
            self.ajouter_transition(etat_puits, symbole, etat_puits)
    
    def afficher(self) -> str:
        """Affichage spécifique aux ADC."""
        return f"ADC:\n{super().afficher()}"


class AFDC(ADC):
    """Automate Fini Déterministe Complet."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        """Initialise un AFDC."""
        super().__init__(alphabet, etats, etat_initial, etats_finaux)
        if not self.est_fini():
            raise ValueError("L'automate doit être fini")
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        return len(self.etats) < float('inf') and len(self.alphabet) < float('inf')
    
    def minimiser(self) -> 'AFDC':
        """Retourne l'automate minimal équivalent."""
        # Algorithme de minimisation par classes d'équivalence
        classes = self._calculer_classes_equivalence()
        return self._construire_automate_minimal(classes)
    
    def _calculer_classes_equivalence(self) -> List[Set[Etat]]:
        """Calcule les classes d'équivalence pour la minimisation."""
        # Partition initiale : états finaux vs non-finaux
        finaux = set(self.etats_finaux)
        non_finaux = self.etats - finaux
        
        partition = []
        if finaux:
            partition.append(finaux)
        if non_finaux:
            partition.append(non_finaux)
        
        # Raffiner la partition
        changed = True
        while changed:
            changed = False
            nouvelle_partition = []
            
            for classe in partition:
                sous_classes = self._raffiner_classe(classe, partition)
                if len(sous_classes) > 1:
                    changed = True
                nouvelle_partition.extend(sous_classes)
            
            partition = nouvelle_partition
        
        return partition
    
    def _raffiner_classe(self, classe: Set[Etat], partition: List[Set[Etat]]) -> List[Set[Etat]]:
        """Raffine une classe d'équivalence."""
        if len(classe) <= 1:
            return [classe]
        
        sous_classes = {}
        for etat in classe:
            signature = []
            for symbole in sorted(self.alphabet):
                transitions = self.obtenir_transitions(etat, symbole)
                if transitions:
                    dest = next(iter(transitions))
                    # Trouver la classe de destination
                    classe_dest = None
                    for i, p in enumerate(partition):
                        if dest in p:
                            classe_dest = i
                            break
                    signature.append(classe_dest)
                else:
                    signature.append(None)
            
            signature_key = tuple(signature)
            if signature_key not in sous_classes:
                sous_classes[signature_key] = set()
            sous_classes[signature_key].add(etat)
        
        return list(sous_classes.values())
    
    def _construire_automate_minimal(self, classes: List[Set[Etat]]) -> 'AFDC':
        """Construit l'automate minimal à partir des classes d'équivalence."""
        # Créer les nouveaux états
        nouveaux_etats = set()
        classe_vers_etat = {}
        
        for i, classe in enumerate(classes):
            nouvel_etat = Etat(f"C{i}")
            nouveaux_etats.add(nouvel_etat)
            classe_vers_etat[i] = nouvel_etat
            
            # Vérifier si c'est un état final
            if any(etat.est_final for etat in classe):
                nouvel_etat.est_final = True
        
        # Trouver l'état initial
        etat_initial_classe = None
        for i, classe in enumerate(classes):
            if self.etat_initial in classe:
                etat_initial_classe = classe_vers_etat[i]
                break
        
        # États finaux
        etats_finaux = {etat for etat in nouveaux_etats if etat.est_final}
        
        # Créer le nouvel automate
        automate_minimal = AFDC(self.alphabet, nouveaux_etats, etat_initial_classe, etats_finaux)
        
        # Ajouter les transitions
        for i, classe in enumerate(classes):
            etat_representant = next(iter(classe))
            etat_source = classe_vers_etat[i]
            
            for symbole in self.alphabet:
                transitions = self.obtenir_transitions(etat_representant, symbole)
                if transitions:
                    dest = next(iter(transitions))
                    # Trouver la classe de destination
                    for j, classe_dest in enumerate(classes):
                        if dest in classe_dest:
                            etat_dest = classe_vers_etat[j]
                            automate_minimal.ajouter_transition(etat_source, symbole, etat_dest)
                            break
        
        return automate_minimal
    
    def complementaire(self) -> 'AFDC':
        """Retourne l'automate complémentaire."""
        # Inverser les états finaux et non-finaux
        nouveaux_etats_finaux = self.etats - self.etats_finaux
        
        # Créer le nouvel automate
        automate_comp = AFDC(self.alphabet.copy(), self.etats.copy(), 
                            self.etat_initial, nouveaux_etats_finaux)
        
        # Copier les transitions
        automate_comp.transitions = self.transitions.copy()
        
        return automate_comp


class AND(Automate):
    """Automate Non Déterministe."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        """Initialise un AND."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Ajoute une transition non déterministe."""
        super().ajouter_transition(etat_source, symbole, etat_cible)
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition non déterministe."""
        super().supprimer_transition(etat_source, symbole, etat_cible)
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        """Retourne un ensemble d'états (non déterminisme)."""
        return super().obtenir_transitions(etat, symbole)
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance non déterministe d'un mot."""
        return super().reconnaitre_mot(mot)
    
    def est_deterministe(self) -> bool:
        """Vérifie le déterminisme."""
        return super().est_deterministe()
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        return super().est_complet()
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        # Construction des sous-ensembles
        nouvel_alphabet = self.alphabet.copy()
        nouveaux_etats = set()
        nouvelles_transitions = {}
        
        # État initial = {etat_initial}
        etat_initial_ensemble = frozenset([self.etat_initial])
        nouveaux_etats.add(etat_initial_ensemble)
        
        # File pour BFS
        file = deque([etat_initial_ensemble])
        traites = set([etat_initial_ensemble])
        
        while file:
            ensemble_courant = file.popleft()
            
            for symbole in self.alphabet:
                # Calculer l'ensemble des états accessibles
                nouvel_ensemble = set()
                for etat in ensemble_courant:
                    nouvel_ensemble.update(self.obtenir_transitions(etat, symbole))
                
                if nouvel_ensemble:
                    nouvel_ensemble_frozen = frozenset(nouvel_ensemble)
                    
                    if nouvel_ensemble_frozen not in traites:
                        nouveaux_etats.add(nouvel_ensemble_frozen)
                        file.append(nouvel_ensemble_frozen)
                        traites.add(nouvel_ensemble_frozen)
                    
                    # Ajouter la transition
                    if ensemble_courant not in nouvelles_transitions:
                        nouvelles_transitions[ensemble_courant] = {}
                    if symbole not in nouvelles_transitions[ensemble_courant]:
                        nouvelles_transitions[ensemble_courant][symbole] = set()
                    nouvelles_transitions[ensemble_courant][symbole].add(nouvel_ensemble_frozen)
        
        # Créer les états du nouvel automate
        etat_mapping = {}
        etats_adc = set()
        
        for i, ensemble in enumerate(nouveaux_etats):
            nom_etat = "{" + ",".join(sorted([str(e) for e in ensemble])) + "}"
            nouvel_etat = Etat(nom_etat)
            etat_mapping[ensemble] = nouvel_etat
            etats_adc.add(nouvel_etat)
        
        # État initial
        etat_initial_adc = etat_mapping[etat_initial_ensemble]
        
        # États finaux (contiennent au moins un état final original)
        etats_finaux_adc = set()
        for ensemble in nouveaux_etats:
            if any(etat.est_final for etat in ensemble):
                etats_finaux_adc.add(etat_mapping[ensemble])
        
        # Créer l'ADC
        adc = ADC(nouvel_alphabet, etats_adc, etat_initial_adc, etats_finaux_adc)
        
        # Ajouter les transitions
        for source, transitions_source in nouvelles_transitions.items():
            for symbole, destinations in transitions_source.items():
                for dest in destinations:
                    adc.ajouter_transition(etat_mapping[source], symbole, etat_mapping[dest])
        
        return adc
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        return f"AND:\n{super().afficher()}"


class AFND(AND):
    """Automate Fini Non Déterministe."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        """Initialise un AFND."""
        super().__init__(alphabet, etats, etat_initial, etats_finaux)
        if not self.est_fini():
            raise ValueError("L'automate doit être fini")
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        return len(self.etats) < float('inf') and len(self.alphabet) < float('inf')
    
    def construction_sous_ensembles(self) -> AFDC:
        """Algorithme de construction des sous-ensembles pour déterminiser."""
        adc = self.determiniser()
        # Convertir ADC en AFDC
        return AFDC(adc.alphabet, adc.etats, adc.etat_initial, adc.etats_finaux)


class AFNS(AFND):
    """Automate Fini à Transitions Spontanées (ε-transitions)."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        """Initialise un AFNS."""
        super().__init__(alphabet, etats, etat_initial, etats_finaux)
        self.epsilon = ""  # Représentation d'epsilon
    
    def ajouter_transition_epsilon(self, etat_source: Etat, etat_cible: Etat) -> None:
        """Ajoute une ε-transition."""
        self.ajouter_transition(etat_source, self.epsilon, etat_cible)
    
    def supprimer_transition_epsilon(self, etat_source: Etat, etat_cible: Etat) -> None:
        """Supprime une ε-transition."""
        self.supprimer_transition(etat_source, self.epsilon, etat_cible)
    
    def epsilon_fermeture(self, etat: Etat) -> Set[Etat]:
        """Calcule l'ε-fermeture d'un état."""
        fermeture = {etat}
        pile = [etat]
        
        while pile:
            etat_courant = pile.pop()
            transitions_epsilon = self.obtenir_transitions(etat_courant, self.epsilon)
            
            for etat_suivant in transitions_epsilon:
                if etat_suivant not in fermeture:
                    fermeture.add(etat_suivant)
                    pile.append(etat_suivant)
        
        return fermeture
    
    def epsilon_fermeture_ensemble(self, ensemble_etats: Set[Etat]) -> Set[Etat]:
        """Calcule l'ε-fermeture d'un ensemble d'états."""
        fermeture = set()
        for etat in ensemble_etats:
            fermeture.update(self.epsilon_fermeture(etat))
        return fermeture
    
    def transiter(self, ensemble_etats: Set[Etat], symbole: str) -> Set[Etat]:
        """Calcule les transitions depuis un ensemble d'états avec un symbole."""
        if symbole == self.epsilon:
            return self.epsilon_fermeture_ensemble(ensemble_etats)
        
        etats_atteignables = set()
        for etat in ensemble_etats:
            etats_atteignables.update(self.obtenir_transitions(etat, symbole))
        
        return self.epsilon_fermeture_ensemble(etats_atteignables)
    
    def construction_sous_ensembles(self) -> AFDC:
        """Construction des sous-ensembles pour un AFNS."""
        nouvel_alphabet = self.alphabet.copy()
        nouvel_alphabet.discard(self.epsilon)  # Retirer epsilon de l'alphabet
        
        nouveaux_etats = set()
        nouvelles_transitions = {}
        
        # État initial = ε-fermeture(etat_initial)
        etat_initial_ensemble = self.epsilon_fermeture(self.etat_initial)
        etat_initial_frozen = frozenset(etat_initial_ensemble)
        nouveaux_etats.add(etat_initial_frozen)
        
        # File pour BFS
        file = deque([etat_initial_frozen])
        traites = set([etat_initial_frozen])
        
        while file:
            ensemble_courant = file.popleft()
            
            for symbole in nouvel_alphabet:
                nouvel_ensemble = self.transiter(set(ensemble_courant), symbole)
                
                if nouvel_ensemble:
                    nouvel_ensemble_frozen = frozenset(nouvel_ensemble)
                    
                    if nouvel_ensemble_frozen not in traites:
                        nouveaux_etats.add(nouvel_ensemble_frozen)
                        file.append(nouvel_ensemble_frozen)
                        traites.add(nouvel_ensemble_frozen)
                    
                    # Ajouter la transition
                    if ensemble_courant not in nouvelles_transitions:
                        nouvelles_transitions[ensemble_courant] = {}
                    if symbole not in nouvelles_transitions[ensemble_courant]:
                        nouvelles_transitions[ensemble_courant][symbole] = set()
                    nouvelles_transitions[ensemble_courant][symbole].add(nouvel_ensemble_frozen)
        
        # Créer les états du nouvel automate
        etat_mapping = {}
        etats_afdc = set()
        
        for i, ensemble in enumerate(nouveaux_etats):
            nom_etat = "{" + ",".join(sorted([str(e) for e in ensemble])) + "}"
            nouvel_etat = Etat(nom_etat)
            etat_mapping[ensemble] = nouvel_etat
            etats_afdc.add(nouvel_etat)
        
        # État initial
        etat_initial_afdc = etat_mapping[etat_initial_frozen]
        
        # États finaux
        etats_finaux_afdc = set()
        for ensemble in nouveaux_etats:
            if any(etat.est_final for etat in ensemble):
                etats_finaux_afdc.add(etat_mapping[ensemble])
        
        # Créer l'AFDC
        afdc = AFDC(nouvel_alphabet, etats_afdc, etat_initial_afdc, etats_finaux_afdc)
        
        # Ajouter les transitions
        for source, transitions_source in nouvelles_transitions.items():
            for symbole, destinations in transitions_source.items():
                for dest in destinations:
                    afdc.ajouter_transition(etat_mapping[source], symbole, etat_mapping[dest])
        
        return afdc
    
    def eliminer_epsilon_transitions(self) -> AFND:
        """Élimine les ε-transitions pour obtenir un AFND équivalent."""
        nouvel_alphabet = self.alphabet.copy()
        nouvel_alphabet.discard(self.epsilon)
        
        # Créer le nouvel automate sans epsilon
        afnd = AFND(nouvel_alphabet, self.etats.copy(), self.etat_initial, set())
        
        # Recalculer les états finaux
        nouveaux_etats_finaux = set()
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            if any(e.est_final for e in fermeture):
                nouveaux_etats_finaux.add(etat)
        
        afnd.etats_finaux = nouveaux_etats_finaux
        
        # Ajouter les nouvelles transitions
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            for symbole in nouvel_alphabet:
                etats_atteignables = set()
                for e in fermeture:
                    etats_atteignables.update(self.obtenir_transitions(e, symbole))
                
                for etat_dest in etats_atteignables:
                    fermeture_dest = self.epsilon_fermeture(etat_dest)
                    for e_dest in fermeture_dest:
                        afnd.ajouter_transition(etat, symbole, e_dest)
        
        return afnd


class AutomateCanonique(AFDC):
    """Automate canonique selon le théorème de Myhill-Nerode."""
    
    def __init__(self, langage: Langage) -> None:
        """Construit l'automate canonique d'un langage."""
        self.langage = langage
        self.classes_equivalence = self._calculer_classes_equivalence()
        
        # Construire l'automate à partir des classes
        alphabet = self._extraire_alphabet()
        etats = self._creer_etats_depuis_classes()
        etat_initial = self._determiner_etat_initial()
        etats_finaux = self._determiner_etats_finaux()
        
        super().__init__(alphabet, etats, etat_initial, etats_finaux)
        self._construire_transitions()
    
    def _extraire_alphabet(self) -> Set[str]:
        """Extrait l'alphabet du langage."""
        alphabet = set()
        for mot in self.langage.mots:
            alphabet.update(set(mot))
        return alphabet
    
    def _calculer_classes_equivalence(self) -> Dict[str, Set[str]]:
        """Calcule les classes d'équivalence à droite."""
        classes = {}
        mots_traites = set()
        
        # Commencer par le mot vide
        mots_a_traiter = [""]
        
        while mots_a_traiter:
            mot = mots_a_traiter.pop(0)
            if mot in mots_traites:
                continue
            
            mots_traites.add(mot)
            classe = self.classe_equivalence(mot)
            representant = min(classe)  # Choisir le plus petit comme représentant
            
            if representant not in classes:
                classes[representant] = classe
                
                # Ajouter les dérivées pour exploration
                for symbole in self._extraire_alphabet():
                    nouveau_mot = mot + symbole
                    if nouveau_mot not in mots_traites:
                        mots_a_traiter.append(nouveau_mot)
        
        return classes
    
    def _creer_etats_depuis_classes(self) -> Set[Etat]:
        """Crée les états depuis les classes d'équivalence."""
        etats = set()
        for representant in self.classes_equivalence:
            etat = Etat(f"[{representant}]")
            etats.add(etat)
        return etats
    
    def _determiner_etat_initial(self) -> Etat:
        """Détermine l'état initial (classe du mot vide)."""
        for etat in self.etats:
            if etat.nom == "[]":  # Classe du mot vide
                return etat
        raise ValueError("État initial non trouvé")
    
    def _determiner_etats_finaux(self) -> Set[Etat]:
        """Détermine les états finaux."""
        etats_finaux = set()
        for representant, classe in self.classes_equivalence.items():
            if any(self.langage.contient(mot) for mot in classe):
                # Trouver l'état correspondant
                for etat in self.etats:
                    if etat.nom == f"[{representant}]":
                        etats_finaux.add(etat)
                        break
        return etats_finaux
    
    def _construire_transitions(self):
        """Construit les transitions entre les états."""
        for representant in self.classes_equivalence:
            etat_source = self._trouver_etat_par_nom(f"[{representant}]")
            
            for symbole in self.alphabet:
                mot_derive = representant + symbole
                classe_dest = self._trouver_classe_contenant(mot_derive)
                
                if classe_dest:
                    etat_dest = self._trouver_etat_par_nom(f"[{classe_dest}]")
                    self.ajouter_transition(etat_source, symbole, etat_dest)
    
    def _trouver_etat_par_nom(self, nom: str) -> Etat:
        """Trouve un état par son nom."""
        for etat in self.etats:
            if etat.nom == nom:
                return etat
        raise ValueError(f"État {nom} non trouvé")
    
    def _trouver_classe_contenant(self, mot: str) -> Optional[str]:
        """Trouve le représentant de la classe contenant un mot."""
        for representant, classe in self.classes_equivalence.items():
            if self.relation_equivalence_droite(mot, representant):
                return representant
        return None
    
    def relation_equivalence_droite(self, mot1: str, mot2: str) -> bool:
        """Vérifie si deux mots sont équivalents à droite."""
        # Deux mots sont équivalents à droite si pour tout suffixe w,
        # mot1.w ∈ L ⟺ mot2.w ∈ L
        
        # Test avec suffixes courants (approximation)
        suffixes_test = ["", "a", "b", "aa", "ab", "ba", "bb"]  # À adapter selon le contexte
        
        for suffixe in suffixes_test:
            mot1_suffixe = mot1 + suffixe
            mot2_suffixe = mot2 + suffixe
            
            if self.langage.contient(mot1_suffixe) != self.langage.contient(mot2_suffixe):
                return False
        
        return True
    
    def classe_equivalence(self, mot: str) -> Set[str]:
        """Retourne la classe d'équivalence d'un mot."""
        classe = {mot}
        
        # Recherche d'autres mots équivalents (approximation)
        mots_candidats = list(self.langage.mots) + [""]
        
        for candidat in mots_candidats:
            if candidat != mot and self.relation_equivalence_droite(mot, candidat):
                classe.add(candidat)
        
        return classe
    
    def nombre_classes_equivalence(self) -> int:
        """Retourne le nombre de classes d'équivalence."""
        return len(self.classes_equivalence)
    
    def construire_depuis_langage(self, langage: Langage) -> None:
        """Reconstruit l'automate depuis un nouveau langage."""
        self.__init__(langage)
    
    def est_minimal(self) -> bool:
        """Vérifie si l'automate est minimal."""
        # Un automate canonique est par définition minimal
        return True




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