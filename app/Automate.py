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
        self.epsilon=""

        if etats is not None:
            self.etats = etats  
        else :
            raise ValueError("Un automate doit avoir des etats")
        
        if etat_initial is not None and etat_initial in self.etats:
            self.etat_initial = etat_initial  
            self.etat_initial.est_initial = True
        else :
            raise ValueError("L'état initial doit être défini et appartenir aux états")
        
        
        if not etats_finaux or not etats_finaux.issubset(self.etats):
            raise ValueError("Tous les états finaux doivent faire partie de l'ensemble des états.")

        else :
            self.etats_finaux = etats_finaux  
            for etat in self.etats_finaux:
                etat.est_final = True
                
    def ajouter_transition(self, source: Etat, symbole: str, destination: Etat):
        """Ajoute une transition à l'automate."""
        if source not in self.transitions:
            self.transitions[source] = {}
        if symbole not in self.transitions[source]:
            self.transitions[source][symbole] = set()
        self.transitions[source][symbole].add(destination)


    def fermeture_epsilon(self, etats: Set[Etat]) -> Set[Etat]:
        """
        Calcule la fermeture epsilon d'un ensemble d'états.
        Utilise '' ou 'ε' comme symbole epsilon.
        """
        fermeture = set(etats)
        pile = list(etats)
        
        while pile:
            etat_courant = pile.pop()
            
            # Vérifier les transitions epsilon ('' ou 'ε')
            for epsilon in ['', 'ε']:
                if (etat_courant in self.transitions and 
                    epsilon in self.transitions[etat_courant]):
                    
                    for etat_destination in self.transitions[etat_courant][epsilon]:
                        if etat_destination not in fermeture:
                            fermeture.add(etat_destination)
                            pile.append(etat_destination)
        
        return fermeture

    def determinisation_thompson(self) -> 'AD':
        """
        Déterminisation par l'algorithme de Thompson.
        Utilise la construction par sous-ensembles avec fermeture epsilon.
        """
        # État initial : fermeture epsilon de l'état initial
        etat_initial_det = self.fermeture_epsilon({self.etat_initial})
        
        # Structures pour la construction
        etats_det = {}  # Dict: frozenset -> Etat
        transitions_det = {}
        etats_a_traiter = deque()
        
        # Créer l'état initial déterministe
        nom_initial = "{" + ",".join(sorted(e.nom for e in etat_initial_det)) + "}"
        etat_initial_automate_det = Etat(nom_initial)
        etats_det[frozenset(etat_initial_det)] = etat_initial_automate_det
        etats_a_traiter.append(etat_initial_det)
        
        while etats_a_traiter:
            ensemble_courant = etats_a_traiter.popleft()
            etat_courant_det = etats_det[frozenset(ensemble_courant)]
            
            # Pour chaque symbole de l'alphabet
            for symbole in self.alphabet:
                if symbole in ['', 'ε']:  # Ignorer epsilon
                    continue
                    
                # Calculer l'ensemble des états accessibles
                etats_accessibles = set()
                
                for etat in ensemble_courant:
                    if (etat in self.transitions and 
                        symbole in self.transitions[etat]):
                        etats_accessibles.update(self.transitions[etat][symbole])
                
                if not etats_accessibles:
                    continue
                
                # Appliquer la fermeture epsilon
                nouvel_ensemble = self.fermeture_epsilon(etats_accessibles)
                
                if not nouvel_ensemble:
                    continue
                
                # Créer ou récupérer l'état déterministe correspondant
                if frozenset(nouvel_ensemble) not in etats_det:
                    nom_nouvel_etat = "{" + ",".join(sorted(e.nom for e in nouvel_ensemble)) + "}"
                    nouvel_etat_det = Etat(nom_nouvel_etat)
                    etats_det[frozenset(nouvel_ensemble)] = nouvel_etat_det
                    etats_a_traiter.append(nouvel_ensemble)
                else:
                    nouvel_etat_det = etats_det[frozenset(nouvel_ensemble)]
                
                # Ajouter la transition
                if etat_courant_det not in transitions_det:
                    transitions_det[etat_courant_det] = {}
                if symbole not in transitions_det[etat_courant_det]:
                    transitions_det[etat_courant_det][symbole] = set()
                transitions_det[etat_courant_det][symbole].add(nouvel_etat_det)
        
        # Déterminer les états finaux
        etats_finaux_det = set()
        for ensemble_etats, etat_det in etats_det.items():
            if any(etat in self.etats_finaux for etat in ensemble_etats):
                etats_finaux_det.add(etat_det)
        
        # Créer l'automate déterministe
        print(self.alphabet,
            set(etats_det.values()),
            etat_initial_automate_det,
            etats_finaux_det
        )

        automate_det = AD(
            alphabet=self.alphabet,
            etats=set(etats_det.values()),
            etat_initial=etat_initial_automate_det,
            etats_finaux=etats_finaux_det
        )
        automate_det.transitions = transitions_det
        
        return automate_det
    
    def determinisation_brzozowski(self) -> 'AD':
        """
        Déterminisation par l'algorithme de Brzozowski.
        Principe: reverse → déterminiser → reverse → déterminiser
        """
        # Étape 1: Inverser l'automate
        automate_inverse = self._inverser()
        
        # Étape 2: Déterminiser l'automate inversé
        automate_inverse_det = automate_inverse._determiniser_construction_sous_ensembles()
        
        # Étape 3: Inverser à nouveau
        automate_inverse_inverse = automate_inverse_det._inverser()
        
        # Étape 4: Déterminiser une dernière fois
        automate_final = automate_inverse_inverse._determiniser_construction_sous_ensembles()
        
        return automate_final

    @staticmethod
    def _inverser(self) -> 'AFND':
        """Inverse l'automate (inverse les transitions et échange initial/finaux)."""
        # Créer un nouvel état initial unique
        nouvel_initial = Etat("init_inverse")
        nouveaux_etats = self.etats.copy()
        nouveaux_etats.add(nouvel_initial)
        
        # Les anciens états finaux deviennent sources vers le nouvel initial
        nouvelles_transitions = {}
        
        # Inverser toutes les transitions
        for source, trans_dict in self.transitions.items():
            for symbole, destinations in trans_dict.items():
                for dest in destinations:
                    if dest not in nouvelles_transitions:
                        nouvelles_transitions[dest] = {}
                    if symbole not in nouvelles_transitions[dest]:
                        nouvelles_transitions[dest][symbole] = set()
                    nouvelles_transitions[dest][symbole].add(source)
        
        # Ajouter transitions depuis nouvel initial vers anciens états finaux
        nouvelles_transitions[nouvel_initial] = {}
        for symbole in self.alphabet:
            nouvelles_transitions[nouvel_initial][symbole] = set()
        
        # Epsilon transitions depuis nouvel initial vers anciens finaux
        if self.epsilon in self.alphabet:
            nouvelles_transitions[nouvel_initial][self.epsilon] = self.etats_finaux.copy()
        
        # Créer l'automate inversé
        automate_inverse = AFND(
            alphabet=self.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux={self.etat_initial}  # Ancien initial devient final
        )
        
        automate_inverse.transitions = nouvelles_transitions
        return automate_inverse

    @staticmethod
    def _determiniser_construction_sous_ensembles(self) -> 'AD':
        """Construction par sous-ensembles standard."""
        from collections import deque
        
        # État initial : fermeture epsilon de l'état initial
        etat_initial_det = self.epsilon_fermeture(self.etat_initial)
        
        # Structures pour la construction
        etats_det = {}
        transitions_det = {}
        etats_a_traiter = deque()
        
        # Créer l'état initial déterministe
        nom_initial = "{" + ",".join(sorted(e.nom for e in etat_initial_det)) + "}"
        etat_initial_automate_det = Etat(nom_initial)
        etats_det[frozenset(etat_initial_det)] = etat_initial_automate_det
        etats_a_traiter.append(etat_initial_det)
        
        while etats_a_traiter:
            ensemble_courant = etats_a_traiter.popleft()
            etat_courant_det = etats_det[frozenset(ensemble_courant)]
            
            for symbole in self.alphabet:
                if symbole == self.epsilon:
                    continue
                    
                etats_accessibles = set()
                for etat in ensemble_courant:
                    etats_accessibles.update(self.obtenir_transitions(etat, symbole))
                
                if not etats_accessibles:
                    continue
                
                # Appliquer la fermeture epsilon
                nouvel_ensemble = set()
                for etat in etats_accessibles:
                    nouvel_ensemble.update(self.epsilon_fermeture(etat))
                
                if not nouvel_ensemble:
                    continue
                
                # Créer ou récupérer l'état déterministe
                if frozenset(nouvel_ensemble) not in etats_det:
                    nom_nouvel_etat = "{" + ",".join(sorted(e.nom for e in nouvel_ensemble)) + "}"
                    nouvel_etat_det = Etat(nom_nouvel_etat)
                    etats_det[frozenset(nouvel_ensemble)] = nouvel_etat_det
                    etats_a_traiter.append(nouvel_ensemble)
                else:
                    nouvel_etat_det = etats_det[frozenset(nouvel_ensemble)]
                
                # Ajouter la transition
                if etat_courant_det not in transitions_det:
                    transitions_det[etat_courant_det] = {}
                if symbole not in transitions_det[etat_courant_det]:
                    transitions_det[etat_courant_det][symbole] = set()
                transitions_det[etat_courant_det][symbole].add(nouvel_etat_det)
        
        # Déterminer les états finaux
        etats_finaux_det = set()
        for ensemble_etats, etat_det in etats_det.items():
            if any(etat in self.etats_finaux for etat in ensemble_etats):
                etats_finaux_det.add(etat_det)
        
        # Créer l'automate déterministe
        automate_det = AD(
            alphabet=self.alphabet - {self.epsilon} if self.epsilon in self.alphabet else self.alphabet,
            etats=set(etats_det.values()),
            etat_initial=etat_initial_automate_det,
            etats_finaux=etats_finaux_det
        )
        automate_det.transitions = transitions_det
        
        return automate_det

    def construire_automate_glushkov(self, regex: str) -> 'AD':
        """
        Construction d'automate par la méthode de Glushkov.
        Produit directement un automate déterministe sans ε-transitions.
        """
        # Étape 1: Analyser l'expression régulière
        regex_augmentee = self._augmenter_regex(regex)
        positions = self._calculer_positions(regex_augmentee)
        
        # Étape 2: Calculer les fonctions First, Last, Follow
        first_pos = self._calculer_first(regex_augmentee, positions)
        last_pos = self._calculer_last(regex_augmentee, positions)
        follow_pos = self._calculer_follow(regex_augmentee, positions)
        
        # Étape 3: Construire l'automate
        # État initial
        etat_initial = Etat("q0")
        etats = {etat_initial}
        
        # Créer un état pour chaque position
        pos_vers_etat = {}
        for pos in positions:
            etat = Etat(f"q{pos}")
            etats.add(etat)
            pos_vers_etat[pos] = etat
        
        # Alphabet
        alphabet = set()
        for pos, symbole in positions.items():
            if symbole != '#':  # Marqueur de fin
                alphabet.add(symbole)
        
        # Transitions depuis l'état initial
        transitions = {}
        transitions[etat_initial] = {}
        
        for symbole in alphabet:
            destinations = set()
            for pos in first_pos:
                if positions[pos] == symbole:
                    destinations.add(pos_vers_etat[pos])
            if destinations:
                transitions[etat_initial][symbole] = destinations
        
        # Transitions entre états
        for pos in positions:
            if positions[pos] == '#':  # Position finale
                continue
                
            etat_source = pos_vers_etat[pos]
            transitions[etat_source] = {}
            
            for symbole in alphabet:
                destinations = set()
                for pos_suiv in follow_pos.get(pos, set()):
                    if positions[pos_suiv] == symbole:
                        destinations.add(pos_vers_etat[pos_suiv])
                if destinations:
                    transitions[etat_source][symbole] = destinations
        
        # États finaux : ceux correspondant aux positions dans Last
        etats_finaux = set()
        for pos in last_pos:
            if positions[pos] == '#':
                etats_finaux.add(etat_initial)  # Si regex accepte mot vide
            else:
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

    @staticmethod
    def _augmenter_regex(regex: str) -> str:
        """Ajoute un marqueur de fin unique à la regex."""
        return f"({regex})#"

    @staticmethod
    def _calculer_positions(regex: str) -> dict:
        """Calcule les positions des symboles dans la regex."""
        positions = {}
        compteur = 1
        
        for char in regex:
            if char.isalnum() or char == '#':
                positions[compteur] = char
                compteur += 1
        
        return positions

    @staticmethod
    def _calculer_first(regex: str, positions: dict) -> set:
        """Calcule l'ensemble First de la regex."""
        # Implémentation simplifiée pour les cas de base
        first = set()
        
        # Pour une implémentation complète, il faudrait parser l'AST de la regex
        # Ici, version simplifiée : premier symbole trouvé
        for pos, symbole in positions.items():
            if symbole != '#':
                first.add(pos)
                break
        
        return first

    @staticmethod
    def _calculer_last(regex: str, positions: dict) -> set:
        """Calcule l'ensemble Last de la regex."""
        # Implémentation simplifiée
        last = set()
        
        # Ajouter la position du marqueur de fin
        for pos, symbole in positions.items():
            if symbole == '#':
                last.add(pos)
        
        return last

    @staticmethod
    def _calculer_follow(regex: str, positions: dict) -> dict:
        """Calcule l'ensemble Follow pour chaque position."""
        # Implémentation simplifiée
        follow = {}
        
        # Pour une implémentation complète, il faudrait analyser
        # les opérateurs de concaténation, union, étoile
        pos_list = list(positions.keys())
        
        for i, pos in enumerate(pos_list[:-1]):
            follow[pos] = {pos_list[i + 1]}
        
        return follow

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

    @staticmethod
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
    
    def matrice_a_automate(self, matrice: list[list]):
        """
        Convertit une matrice de transitions en un automate.
        Args:
            matrice: Liste de listes où matrice[i][j] contient les indices des états destinations
                    pour l'état i et le symbole j de l'alphabet.
        """
        if not matrice or not matrice[0]:
            raise ValueError("Matrice invalide")

        n = len(matrice)  # Nombre d'états
        m = len(matrice[0])  # Nombre de symboles

        # Créer un alphabet par défaut (par exemple, 'a', 'b', ..., ou utiliser un alphabet donné)
        alphabet = {chr(97 + j) for j in range(m)}  # 'a', 'b', etc.
        
        # Créer les états
        etats = {Etat(f"q{i}") for i in range(n)}
        
        # Identifier l'état initial (par convention, q0)
        etat_initial = next(e for e in etats if e.nom == "q0")
        etat_initial.est_initial = True
        
        # Identifier les états finaux (par exemple, dernier état ou configurable)
        # Convention : dernier état est final (peut être modifié selon le contexte)
        etats_finaux = {next(e for e in etats if e.nom == f"q{n-1}")}
        for e in etats_finaux:
            e.est_final = True
        
        # Initialiser l'automate
        self.alphabet = alphabet
        self.etats = etats
        self.etat_initial = etat_initial
        self.etats_finaux = etats_finaux
        self.transitions = {}
        
        # Ajouter les transitions à partir de la matrice
        alphabet_list = sorted(list(alphabet))
        for i in range(n):
            source = next(e for e in etats if e.nom == f"q{i}")
            for j in range(m):
                symbole = alphabet_list[j]
                for dest_idx in matrice[i][j]:
                    if dest_idx < n:
                        destination = next(e for e in etats if e.nom == f"q{dest_idx}")
                        self.ajouter_transition(source, symbole, destination)
    

class AD(Automate):
    """Automate Déterministe."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_deterministe():
            raise ValueError("L'automate doit être déterministe")
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Ajoute une transition en respectant le déterminisme."""
        if etat_source in self.transitions and symbole in self.transitions[etat_source]:
            if self.transitions[etat_source][symbole]:
                raise ValueError("Transition déjà définie - violation du déterminisme")
        super().ajouter_transition(etat_source, symbole, etat_cible)
    
    def est_deterministe(self) -> bool:
        """Retourne toujours True pour un AD."""
        return True
    

class ADC(AD):
    """Automate Déterministe Complet."""
    
    def __init__(self, alphabet: Set[str], etats: Set[Etat], etat_initial: Etat, 
                 etats_finaux: Set[Etat]) -> None:
        super().__init__(alphabet, etats, etat_initial, etats_finaux)
        self.completer()
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition en maintenant la complétude."""
        super().supprimer_transition(etat_source, symbole, etat_cible)
        self.completer()
    
    def est_complet(self) -> bool:
        """Retourne toujours True pour un ADC."""
        return True
    
    def completer(self) -> None:
        """Complète l'automate."""
        if super().est_complet():
            return
        
        etat_puits = Etat("puits")
        self.etats.add(etat_puits)
        
        for etat in self.etats:
            for symbole in self.alphabet:
                if not super().obtenir_transitions(etat, symbole):
                    super().ajouter_transition(etat, symbole, etat_puits)

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
    
    def __minisiation__optim(self)  -> 'AFDC':
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
    


    def minimiser(self) -> 'AFDC':
        """Retourne l'automate minimal équivalent."""
        # Algorithme de minimisation par classes d'équivalence
        classes = self._calculer_classes_equivalence()
        return self._construire_automate_minimal(classes)
    
    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
    def afficher(self) -> str:
        return "[ADC] " + super().afficher()




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
        return self.determinisation_thompson()
    
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
        if etat is None:
            return set()
        
        fermeture = {etat}
        pile = deque([etat])
        
        while pile:
            etat_courant = pile.pop()
            for etat_suivant in self.obtenir_transitions(etat_courant, self.epsilon):
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
        """Élimine les ε-transitions pour obtenir un AFND équivalent"""
        # Calcul des nouvelles transitions
        nouvelles_transitions = {}
        
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            nouvelles_transitions[etat] = {}
            
            for symbole in self.alphabet - {''}:
                # Calcul des états atteints via symbole + ε-fermeture
                dests = set()
                for e in fermeture:
                    if e in self.transitions and symbole in self.transitions[e]:
                        dests.update(self.transitions[e][symbole])
                
                if dests:
                    dests = self.epsilon_fermeture_ensemble(dests)
                    nouvelles_transitions[etat][symbole] = dests
        
        # Création du nouvel automate
        nouvel_initial = self.etat_initial
        
        # Gestion des états finaux
        nouveaux_finaux = {
            etat 
            for etat in self.etats
            if any(e in self.etats_finaux for e in self.epsilon_fermeture(etat))
        }
        
        # Créer AFND avec constructeur correct
        afnd = AFND(
            alphabet=self.alphabet - {''},  # Retirer epsilon
            etats_finaux=nouveaux_finaux,
            etats=self.etats,
            etat_initial=nouvel_initial
        )
        
        # Ajout des nouvelles transitions
        for source, trans in nouvelles_transitions.items():
            for symbole, dests in trans.items():
                for dest in dests:
                    afnd.ajouter_transition(source, symbole, dest)
        
        return afnd
    


class MinimisateurAutomate:
    """Responsable de la minimisation d'automates existants."""
    
    def __init__(self, automate: AFDC):
        self.automate = automate
    
    def minimiser_par_fusion(self) -> 'AutomateMinimal':
        """Minimise un automate par fusion d'états équivalents."""
        # Algorithme de minimisation par table de marquage
        etats_equivalents = self._calculer_etats_equivalents()
        return self._construire_automate_minimal(etats_equivalents)
    
    @staticmethod
    def _calculer_etats_equivalents(self) -> Dict[Etat, Set[Etat]]:
        """Calcule les classes d'états équivalents par l'algorithme de Moore."""
        etats = list(self.automate.etats)
        n = len(etats)
        
        # Table de marquage pour les paires d'états non-équivalents
        table_marquage = {}
        for i in range(n):
            for j in range(i + 1, n):
                table_marquage[(etats[i], etats[j])] = False
        
        # Phase 1: Marquer les paires (final, non-final)
        for i in range(n):
            for j in range(i + 1, n):
                etat1, etat2 = etats[i], etats[j]
                if (etat1 in self.automate.etats_finaux) != (etat2 in self.automate.etats_finaux):
                    table_marquage[(etat1, etat2)] = True
        
        # Phase 2: Marquer récursivement les paires distinguables
        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(i + 1, n):
                    etat1, etat2 = etats[i], etats[j]
                    if not table_marquage[(etat1, etat2)]:
                        for symbole in self.automate.alphabet:
                            dest1 = self._obtenir_destination(etat1, symbole)
                            dest2 = self._obtenir_destination(etat2, symbole)
                            
                            if dest1 and dest2 and dest1 != dest2:
                                paire = (min(dest1, dest2, key=lambda x: x.nom), 
                                        max(dest1, dest2, key=lambda x: x.nom))
                                if paire in table_marquage and table_marquage[paire]:
                                    table_marquage[(etat1, etat2)] = True
                                    changed = True
                                    break
        
        # Construire les classes d'équivalence
        classes = {}
        traites = set()
        
        for etat in etats:
            if etat not in traites:
                classe = {etat}
                for autre_etat in etats:
                    if autre_etat != etat and autre_etat not in traites:
                        paire = (min(etat, autre_etat, key=lambda x: x.nom),
                                max(etat, autre_etat, key=lambda x: x.nom))
                        if paire in table_marquage and not table_marquage[paire]:
                            classe.add(autre_etat)
                
                representant = min(classe, key=lambda x: x.nom)
                classes[representant] = classe
                traites.update(classe)
        
        return classes
    
    @staticmethod
    def _obtenir_destination(self, etat: Etat, symbole: str) -> Optional[Etat]:
        """Obtient l'état de destination pour une transition donnée."""
        for source, sym, dest in self.automate.transitions:
            if source == etat and sym == symbole:
                return dest
        return None
    
    @staticmethod
    def _construire_automate_minimal(self, classes_etats: Dict[Etat, Set[Etat]]) -> 'AutomateMinimal':
        """Construit l'automate minimal à partir des classes d'états."""
        # Créer les nouveaux états
        nouveaux_etats = set()
        mapping_etats = {}
        
        for representant, classe in classes_etats.items():
            nouvel_etat = Etat(f"M{representant.nom}")
            nouveaux_etats.add(nouvel_etat)
            for etat in classe:
                mapping_etats[etat] = nouvel_etat
        
        # Déterminer l'état initial
        nouvel_etat_initial = mapping_etats[self.automate.etat_initial]
        
        # Déterminer les états finaux
        nouveaux_etats_finaux = set()
        for etat_final in self.automate.etats_finaux:
            nouveaux_etats_finaux.add(mapping_etats[etat_final])
        
        # Créer l'automate minimal temporaire
        automate_temp = AFDC(
            self.automate.alphabet,
            nouveaux_etats,
            nouvel_etat_initial,
            nouveaux_etats_finaux
        )
        
        # Construire les transitions
        transitions_ajoutees = set()
        for source, symbole, dest in self.automate.transitions:
            nouvelle_source = mapping_etats[source]
            nouvelle_dest = mapping_etats[dest]
            
            transition = (nouvelle_source, symbole, nouvelle_dest)
            if transition not in transitions_ajoutees:
                automate_temp.ajouter_transition(nouvelle_source, symbole, nouvelle_dest)
                transitions_ajoutees.add(transition)
        
        return automate_temp


class AutomateMinimal(AFDC):
    """Automate minimal obtenu par minimisation d'un automate existant."""
    
    def __init__(self, automate_source: AFDC):
        """Construit un automate minimal à partir d'un automate existant."""
        self.automate_source = automate_source
        minimisateur = MinimisateurAutomate(automate_source)
        
        # Minimiser l'automate source
        automate_minimal = minimisateur.minimiser_par_fusion()
        
        # Initialiser avec les composants minimisés
        super().__init__(
            automate_minimal.alphabet,
            automate_minimal.etats,
            automate_minimal.etat_initial,
            automate_minimal.etats_finaux
        )
        self.transitions = automate_minimal.transitions
    
    def est_minimal(self) -> bool:
        """Vérifie si l'automate est minimal."""
        return self._aucun_etat_equivalent()
    
    @staticmethod
    def _aucun_etat_equivalent(self) -> bool:
        """Vérifie qu'aucun état n'est équivalent à un autre."""
        if not isinstance(self.etats, set) or len(self.etats) <= 1:
            return True
        
        etats = list(self.etats)
        n = len(etats)
        
        # Vérifier chaque paire d'états
        for i in range(n):
            for j in range(i + 1, n):
                if self._etats_equivalents(etats[i], etats[j]):
                    return False
        return True
    
    @staticmethod
    def _etats_equivalents(self, etat1: Etat, etat2: Etat) -> bool:
        """Vérifie si deux états sont équivalents."""
        # États équivalents si même finalité et même comportement
        if (etat1 in self.etats_finaux) != (etat2 in self.etats_finaux):
            return False
        
        # Vérifier les transitions pour chaque symbole
        for symbole in self.alphabet:
            dest1 = self._obtenir_destination(etat1, symbole)
            dest2 = self._obtenir_destination(etat2, symbole)
            
            # Si l'une des destinations n'existe pas
            if (dest1 is None) != (dest2 is None):
                return False
            
            # Si les destinations sont différentes (analyse superficielle)
            if dest1 and dest2 and dest1 != dest2:
                return False
        
        return True
    
    @staticmethod
    def _obtenir_destination(self, etat: Etat, symbole: str) -> Optional[Etat]:
        """Obtient l'état de destination pour une transition donnée."""
        for source, sym, dest in self.transitions:
            if source == etat and sym == symbole:
                return dest
        return None
    
    def nombre_etats_reduits(self) -> int:
        """Retourne le nombre d'états réduits par la minimisation."""
        return len(self.automate_source.etats) - len(self.etats)
    
    def ratio_reduction(self) -> float:
        """Retourne le ratio de réduction des états."""
        if len(self.automate_source.etats) == 0:
            return 0.0
        return self.nombre_etats_reduits() / len(self.automate_source.etats)






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

